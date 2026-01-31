import os
import json
import logging
import hashlib
from datetime import datetime, timezone
from functools import lru_cache

import requests
import psycopg2
import azure.functions as func
import azurefunctions.extensions.bindings.eventhub as eh
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# Azure Functions App V2

app = func.FunctionApp()

# Key Vault + Postgres config

@lru_cache(maxsize=1)
def get_db_config():
    credential = DefaultAzureCredential()
    kv = SecretClient(
        vault_url=os.environ["KEYVAULT_URL"],
        credential=credential
    )

    return {
        "user": os.environ["POSTGRES_USER"],
        "password": kv.get_secret(
            os.environ["POSTGRES_PASSWORD_SECRET"]
        ).value,
        "dbname": os.environ["POSTGRES_DB"],
        "host": os.environ["POSTGRES_HOST"],
        "port": 5432,
        "sslmode": "require",
    }

# SendGrid alert helper

ALERT_FROM = "alerts@azure-streaming243-alerts.com"


def send_alert_email(subject, body):

    api_key = os.environ.get("SENDGRID_API_KEY")
    to_email = os.environ.get("ALERT_TO_EMAIL")

    if not api_key:
        logging.error("SENDGRID_API_KEY not configured")
        return

    if not to_email:
        logging.error("ALERT_TO_EMAIL not configured")
        return

    message = Mail(
        from_email=ALERT_FROM,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
    )

    try:
        sg = SendGridAPIClient(api_key)
        sg.send(message)
    except Exception:
        logging.exception("SendGrid send failed")

# Alerts (Postgres query + rules)


def run_alerts_from_postgres(cur):

    # latest air temperature (weather)
    cur.execute("""
        SELECT
            wr.temperature
        FROM weather_reading wr
        ORDER BY wr.event_time DESC
        LIMIT 1
    """)
    weather = cur.fetchone()

    air_temp_k = weather[0] if weather else None
    air_temp_c = air_temp_k - 273.15 if air_temp_k is not None else None

    # latest iot
    cur.execute("""
        SELECT
            temperature,
            humidity,
            water_level
        FROM iot_reading
        ORDER BY event_time DESC
        LIMIT 1
    """)
    iot = cur.fetchone()

    if not iot:
        return

    soil_temp, soil_humidity, water_level = iot

    alerts = []

    # Air temperature
    if air_temp_c is not None:
        if air_temp_c > 40:
            alerts.append(f"Heat alert – air temperature {air_temp_c:.1f} °C")
        if air_temp_c < 5:
            alerts.append(f"Frost / cold alert – air temperature {air_temp_c:.1f} °C")

    # Water level
    if water_level is not None:
        if water_level < 20:
            alerts.append(f"Low water alert – water level {water_level:.1f} %")

    # Soil humidity
    if soil_humidity is not None:
        if soil_humidity > 80:
            alerts.append(f"Over-watering alert – soil humidity {soil_humidity:.1f} %")
        if soil_humidity < 30:
            alerts.append(f"Dry soil alert – soil humidity {soil_humidity:.1f} %")

    # Soil temperature
    if soil_temp is not None:
        if soil_temp > 35:
            alerts.append(f"Soil too hot alert – soil temperature {soil_temp:.1f} °C")
        if soil_temp < 10:
            alerts.append(f"Soil too cold alert – soil temperature {soil_temp:.1f} °C")

    if not alerts:
        return

    body = (
        "IoT / Weather alerts triggered at "
        f"{datetime.now(timezone.utc).isoformat()}\n\n"
        + "\n".join(alerts)
    )

    send_alert_email(
        subject="IoT platform alert",
        body=body
    )

# TIMER +  Fetch Weather +  Event Hub

@app.function_name(name="fetchweatherapi")
@app.timer_trigger(
    schedule="0 * * * * *",
    arg_name="myTimer",
    run_on_startup=False
)
@app.event_hub_output(
    arg_name="eventhub",
    event_hub_name="streaming_iot_time_series",
    connection="EVENT_HUB_CONNECTION"
)
def fetchweatherapi(myTimer: func.TimerRequest, eventhub: func.Out[str]) -> None:
    if myTimer.past_due:
        logging.warning("Timer is past due")

    KEYVAULT_URL = "https://kv-Az-TimeSeries.vault.azure.net/"

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    city = "windhoek"

    try:
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=KEYVAULT_URL, credential=credential)
        api_key_secret = secret_client.get_secret("weather-api-key")
        API_KEY = api_key_secret.value

        response = requests.get(BASE_URL, params={"appid": API_KEY, "q": city})
        response.raise_for_status()
        data = response.json()

        event_time = datetime.fromtimestamp(
            data["dt"], tz=timezone.utc
        ).replace(microsecond=0)

        event_id = hashlib.sha256(
            f"weather|windhoek|{event_time.isoformat()}".encode()
        ).hexdigest()

        eventhub.set(json.dumps({
            "event_id": event_id,
            "event_type": "weather",
            "event_time": event_time.isoformat(),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "payload": data
        }))

        logging.info("Weather data sent to Event Hub")

    except Exception:
        logging.exception("fetchweatherapi failed")



# EVENT HUB +  POSTGRES

@app.function_name(name="eventhub_to_postgres")
@app.event_hub_message_trigger(
    arg_name="event",
    event_hub_name="streaming_iot_time_series",
    connection="EVENT_HUB_CONNECTION"
)
def eventhub_to_postgres(event: eh.EventData):

    try:
        payload = json.loads(event.body_as_str())
    except Exception:
        logging.exception("Invalid Event Hub message")
        return

    event_type = payload.get("event_type")

    if event_type == "weather":
        handle_weather(payload)
    elif event_type == "iot":
        handle_iot(payload)
    else:
        logging.info("Unknown event type, skipping")

# WEATHER HANDLER

def handle_weather(event: dict):
    data = event["payload"]
    cfg = get_db_config()
    conn = None

    try:
        conn = psycopg2.connect(**cfg)
        cur = conn.cursor()

        # Location UPSERT
        cur.execute("""
            INSERT INTO location (city_name, country_code, latitude, longitude, timezone_offset)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (city_name, country_code)
            DO UPDATE SET
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                timezone_offset = EXCLUDED.timezone_offset
            RETURNING location_id
        """, (
            data["name"],
            data["sys"]["country"],
            data["coord"]["lat"],
            data["coord"]["lon"],
            data["timezone"]
        ))
        location_id = cur.fetchone()[0]

        # Weather condition UPSERT
        w = data["weather"][0]
        cur.execute("""
            INSERT INTO weather_condition (
                external_condition_id, main, description, icon
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (external_condition_id, icon)
            DO UPDATE SET
                main = EXCLUDED.main,
                description = EXCLUDED.description
            RETURNING weather_condition_id
        """, (
            w["id"],
            w["main"],
            w["description"],
            w["icon"]
        ))
        weather_condition_id = cur.fetchone()[0]

        # Weather reading
        cur.execute("""
            INSERT INTO weather_reading (
                event_time,
                location_id,
                weather_condition_id,
                temperature,
                feels_like,
                pressure,
                humidity,
                wind_speed,
                wind_deg,
                visibility,
                cloudiness
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            datetime.fromtimestamp(data["dt"], tz=timezone.utc),
            location_id,
            weather_condition_id,
            data["main"]["temp"],
            data["main"]["feels_like"],
            data["main"]["pressure"],
            data["main"]["humidity"],
            data["wind"]["speed"],
            data["wind"]["deg"],
            data.get("visibility"),
            data["clouds"]["all"]
        ))

        conn.commit()

        # ALERTS
        run_alerts_from_postgres(cur)

        logging.info("Weather data written to Postgres")

    except Exception:
        logging.exception("Weather ingestion failed")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

# IOT + ACTUATOR HANDLER

def handle_iot(event: dict):
    data = event["payload"]
    cfg = get_db_config()
    conn = None

    ACTUATOR_MAP = {
        "fan": {
            "on": "fan_actuator_on",
            "off": "fan_actuator_off",
            "type": "fan"
        },
        "watering_pump": {
            "on": "watering_pump_on",
            "off": "watering_pump_off",
            "type": "pump"
        },
        "water_pump": {
            "on": "water_pump_on",
            "off": "water_pump_off",
            "type": "pump"
        }
    }

    try:
        conn = psycopg2.connect(**cfg)
        cur = conn.cursor()

        event_time = datetime.fromisoformat(
            data["measurement_time"]
        ).replace(tzinfo=timezone.utc)

        location_id = None

        # Insert IoT sensor reading
        cur.execute("""
            INSERT INTO iot_reading (
                event_time,
                location_id,
                temperature,
                humidity,
                water_level,
                nitrogen,
                phosphorus,
                potassium
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (event_time, location_id) DO NOTHING
        """, (
            event_time,
            location_id,
            data.get("temperature"),
            data.get("humidity"),
            data.get("water_level"),
            data.get("nitrogen"),
            data.get("phosphorus"),
            data.get("potassium")
        ))

        # Insert actuator events
        for name, cfg_map in ACTUATOR_MAP.items():
            on_flag = data.get(cfg_map["on"])
            off_flag = data.get(cfg_map["off"])

            if on_flag is None and off_flag is None:
                continue

            if on_flag == 1:
                state = True
            elif off_flag == 1:
                state = False
            else:
                continue

            cur.execute("""
                INSERT INTO actuator (actuator_name, actuator_type)
                VALUES (%s, %s)
                ON CONFLICT (actuator_name)
                DO UPDATE SET actuator_type = EXCLUDED.actuator_type
                RETURNING actuator_id
            """, (name, cfg_map["type"]))
            actuator_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO actuator_event (
                    event_time,
                    actuator_id,
                    state,
                    source
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                event_time,
                actuator_id,
                state,
                "iot"
            ))

        conn.commit()

        # ALERTS
        run_alerts_from_postgres(cur)

        logging.info("IoT + actuator data written to Postgres")

    except Exception:
        logging.exception("IoT ingestion failed")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


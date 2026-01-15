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



# TIMER → Fetch Weather → Event Hub

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

        logging.info(f"Weather data for {city}: {data} and this have been send to even_hub as well")

    except Exception:
        logging.exception("fetchweatherapi failed")



# EVENT HUB → POSTGRES

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

        # Weather reading (deduplicated by index)
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

        location_id = None  # nullable by design

        # IoT sensor data
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

        # Actuator events
        for name, cfg_map in ACTUATOR_MAP.items():
            on_flag = data.get(cfg_map["on"])
            off_flag = data.get(cfg_map["off"])

            if on_flag is None and off_flag is None:
                continue

            state = True if on_flag == 1 else False

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
        logging.info("IoT + actuator data written to Postgres")

    except Exception:
        logging.exception("IoT ingestion failed")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
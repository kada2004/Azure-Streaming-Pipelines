import logging
import json
import hashlib
import os
from datetime import datetime, timezone
from functools import lru_cache

import azure.functions as func
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient



@lru_cache(maxsize=1)
def get_db_config():
    credential = DefaultAzureCredential()
    kv = SecretClient(
        vault_url=os.environ["KEYVAULT_URL"],
        credential=credential
    )
    return {
        "user": os.environ["POSTGRES_USER"],
        "password": kv.get_secret(os.environ["POSTGRES_PASSWORD_SECRET"]).value,
        "dbname": os.environ["POSTGRES_DB"],
        "host": os.environ["POSTGRES_HOST"],
        "port": 5432,
        "sslmode": "require",
    }


# ────────────────────────────────────────────────
#   TIMER → Fetch Weather → Event Hub
# ────────────────────────────────────────────────

app = func.FunctionApp()


@app.function_name(name="fetchweatherapi")
@app.timer_trigger(
    schedule="0 * * * * *",   # every minute – consider 0 */5 * * * * for production
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
        logging.warning("Timer is past due!")

    try:
        credential = DefaultAzureCredential()
        kv = SecretClient(
            vault_url="https://kv-Az-TimeSeries.vault.azure.net/",
            credential=credential
        )
        api_key = kv.get_secret("weather-api-key").value

        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"appid": api_key, "q": "windhoek", "units": "metric"},
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        event_time = datetime.fromtimestamp(data["dt"], tz=timezone.utc).replace(microsecond=0)
        event_id = hashlib.sha256(
            f"weather|windhoek|{event_time.isoformat()}".encode()
        ).hexdigest()

        event_payload = {
            "event_id": event_id,
            "event_type": "weather",
            "event_time": event_time.isoformat(),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "payload": data
        }

        eventhub.set(json.dumps(event_payload))
        logging.info(f"Weather event sent to Event Hub – city: windhoek, time: {event_time}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch weather from OpenWeatherMap: {e}")
    except Exception:
        logging.exception("fetchweatherapi failed unexpectedly")



#   Event Hub → PostgreSQL 


@app.function_name(name="eventhub_to_postgres")
@app.event_hub_trigger(
    arg_name="event",
    event_hub_name="streaming_iot_time_series",
    connection="EVENT_HUB_CONNECTION"
)
def eventhub_to_postgres(event: func.EventHubEvent):
    try:
        payload = json.loads(event.get_body().decode("utf-8"))
    except Exception:
        logging.exception("Failed to parse Event Hub message")
        return

    if payload.get("event_type") != "weather":
        logging.info("Skipping non-weather event")
        return

    data = payload["payload"]

    import psycopg
    from psycopg import sql

    cfg = get_db_config()
    conn = None

    try:
        conn = psycopg.connect(**cfg, autocommit=True)
        with conn.cursor() as cur:

            # 1. UPSERT location
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

            # 2. INSERT weather reading (idempotent)
            cur.execute("""
                INSERT INTO weather_reading (
                    event_time,
                    location_id,
                    temperature,
                    humidity,
                    event_id
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (event_id) DO NOTHING
            """, (
                datetime.fromtimestamp(data["dt"], tz=timezone.utc),
                location_id,
                data["main"]["temp"],
                data["main"]["humidity"],
                payload["event_id"]              # prevents duplicates
            ))

        logging.info(f"Successfully wrote weather data to Postgres – location_id={location_id}")

    except psycopg.Error as e:
        logging.error(f"PostgreSQL error: {e.pgerror or e}")
    except Exception:
        logging.exception("Failed to write to Postgres")
    finally:
        if conn:
            conn.close()
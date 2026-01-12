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

app = func.FunctionApp()


#  TIMER FUNCTION 

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
    try:
        credential = DefaultAzureCredential()
        kv = SecretClient(
            vault_url="https://kv-Az-TimeSeries.vault.azure.net/",
            credential=credential
        )

        api_key = kv.get_secret("weather-api-key").value

        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"appid": api_key, "q": "windhoek"},
            timeout=20
        )
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

        logging.info("Weather event sent to Event Hub")

    except Exception:
        logging.exception("fetchweatherapi failed")



#  ASYNCPG CONNECTION (LAZY + SAFE)


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
        "database": os.environ["POSTGRES_DB"],
        "host": os.environ["POSTGRES_HOST"],
        "port": 5432,
        "ssl": "require",
    }



#  EVENT HUB → POSTGRES (ASYNC, SAFE)


@app.function_name(name="eventhub_to_postgres")
@app.event_hub_trigger(
    arg_name="event",
    event_hub_name="streaming_iot_time_series",
    connection="EVENT_HUB_CONNECTION"
)
async def eventhub_to_postgres(event: func.EventHubEvent):

    try:
        payload = json.loads(event.get_body().decode())
    except Exception:
        logging.exception("Invalid Event Hub message")
        return

    if payload.get("event_type") != "weather":
        return

    import asyncpg  # imported inside function

    data = payload["payload"]
    cfg = get_db_config()

    conn = None
    try:
        conn = await asyncpg.connect(**cfg)

        # Location UPSERT
        location_id = await conn.fetchval("""
            INSERT INTO location (city_name, country_code, latitude, longitude, timezone_offset)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (city_name, country_code)
            DO UPDATE SET
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude
            RETURNING location_id
        """,
            data["name"],
            data["sys"]["country"],
            data["coord"]["lat"],
            data["coord"]["lon"],
            data["timezone"],
        )

        # Weather reading INSERT
        await conn.execute("""
            INSERT INTO weather_reading (
                event_time,
                location_id,
                temperature,
                humidity
            )
            VALUES ($1, $2, $3, $4)
            ON CONFLICT DO NOTHING
        """,
            datetime.fromtimestamp(data["dt"], tz=timezone.utc),
            location_id,
            data["main"]["temp"],
            data["main"]["humidity"],
        )

    except Exception:
        logging.exception("Failed to write Event Hub data to Postgres")

    finally:
        if conn:
            await conn.close()

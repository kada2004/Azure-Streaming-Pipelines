import logging
import json
import hashlib
from datetime import datetime, timezone
from functools import lru_cache
import os

import azure.functions as func
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = func.FunctionApp()


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
        logging.info("The timer is past due!")

    KEYVAULT_URL = "https://kv-Az-TimeSeries.vault.azure.net/"
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    city = "windhoek"

    try:
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=KEYVAULT_URL, credential=credential)

        api_key = secret_client.get_secret("weather-api-key").value

        response = requests.get(
            BASE_URL,
            params={"appid": api_key, "q": city},
            timeout=20
        )
        response.raise_for_status()
        data = response.json()

        event_time = datetime.fromtimestamp(
            data["dt"], tz=timezone.utc
        ).replace(microsecond=0)

        raw_id = f"weather|{city}|{event_time.isoformat()}"
        event_id = hashlib.sha256(raw_id.encode()).hexdigest()

        eventhub.set(json.dumps({
            "event_id": event_id,
            "event_type": "weather",
            "schema_version": 1,
            "event_time": event_time.isoformat(),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "payload": data
        }))

        logging.info("Weather event sent to Event Hub")

    except Exception:
        logging.exception("Failed to fetch or publish weather data")


# DATABASE HELPERS (LAZY + SAFE)


@lru_cache(maxsize=1)
def get_engine():
    """
    Engine is created lazily.
    This function is NEVER executed during indexing.
    """
    from sqlalchemy import create_engine  # lazy import

    credential = DefaultAzureCredential()
    kv = SecretClient(
        vault_url=os.environ["KEYVAULT_URL"],
        credential=credential
    )

    password = kv.get_secret(
        os.environ["POSTGRES_PASSWORD_SECRET"]
    ).value

    conn_str = (
        f"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{password}"
        f"@{os.environ['POSTGRES_HOST']}:5432/{os.environ['POSTGRES_DB']}"
        f"?sslmode={os.environ['POSTGRES_SSLMODE']}"
    )

    return create_engine(conn_str, pool_pre_ping=True)


def get_tables():
    """
    Tables are defined lazily.
    SQLAlchemy is imported ONLY when needed.
    """
    from sqlalchemy import (
        MetaData, Table, Column,
        Integer, BigInteger, Text, DECIMAL, TIMESTAMP
    )

    metadata = MetaData(schema="public")

    location = Table(
        "location", metadata,
        Column("location_id", BigInteger, primary_key=True),
        Column("city_name", Text),
        Column("country_code", Text),
        Column("latitude", DECIMAL(9, 6)),
        Column("longitude", DECIMAL(9, 6)),
        Column("timezone_offset", Integer),
    )

    weather_reading = Table(
        "weather_reading", metadata,
        Column("weather_reading_id", BigInteger, primary_key=True),
        Column("event_time", TIMESTAMP(timezone=True)),
        Column("location_id", BigInteger),
        Column("temperature", DECIMAL(5, 2)),
        Column("humidity", Integer),
    )

    return location, weather_reading


# function to DB

@app.function_name(name="eventhub_to_postgres")
@app.event_hub_trigger(
    arg_name="event",
    event_hub_name="streaming_iot_time_series",
    connection="EVENT_HUB_CONNECTION"
)
def eventhub_to_postgres(event: func.EventHubEvent):

    try:
        payload = json.loads(event.get_body().decode())
    except Exception:
        logging.exception("Invalid Event Hub message")
        return

    if payload.get("event_type") != "weather":
        return

    try:
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        engine = get_engine()
        location, weather_reading = get_tables()

        data = payload["payload"]

        with engine.begin() as conn:
            # Location UPSERT
            loc_stmt = (
                pg_insert(location)
                .values(
                    city_name=data["name"],
                    country_code=data["sys"]["country"],
                    latitude=data["coord"]["lat"],
                    longitude=data["coord"]["lon"],
                    timezone_offset=data["timezone"],
                )
                .on_conflict_do_nothing()
                .returning(location.c.location_id)
            )

            location_id = conn.execute(loc_stmt).scalar()

            # Weather insert
            conn.execute(
                pg_insert(weather_reading)
                .values(
                    event_time=datetime.fromtimestamp(
                        data["dt"], tz=timezone.utc
                    ),
                    location_id=location_id,
                    temperature=data["main"]["temp"],
                    humidity=data["main"]["humidity"],
                )
                .on_conflict_do_nothing()
            )

    except Exception:
        logging.exception("Failed to persist Event Hub message to Postgres")

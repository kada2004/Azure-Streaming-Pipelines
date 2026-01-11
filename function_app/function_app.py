import os
import json
import logging
import hashlib
from datetime import datetime, timezone
from functools import lru_cache

import requests
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    Integer, BigInteger, Text, DECIMAL, TIMESTAMP, select
)
from sqlalchemy.dialects.postgresql import insert as pg_insert


app = func.FunctionApp()


# Fetch Weather API -> Event Hub

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

        api_key_secret = secret_client.get_secret("weather-api-key")
        API_KEY = api_key_secret.value

        response = requests.get(BASE_URL, params={"appid": API_KEY, "q": city}, timeout=20)
        response.raise_for_status()
        data = response.json()

        event_time = datetime.fromtimestamp(data["dt"], tz=timezone.utc).replace(microsecond=0)
        raw_id = f"weather|{city}|{event_time.isoformat()}"
        event_id = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()

        event = {
            "event_id": event_id,
            "event_type": "weather",
            "schema_version": 1,
            "event_time": event_time.isoformat(),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "payload": data
        }

        eventhub.set(json.dumps(event))
        logging.info(f"Weather data sent to Event Hub for city={city}, event_id={event_id}")

    except Exception as e:
        logging.exception(f"Error fetching weather data: {e}")



# Database engine (lazy + cached) using Key Vault

@lru_cache(maxsize=1)
def get_engine():
    credential = DefaultAzureCredential()

    secret_client = SecretClient(
        vault_url=os.environ["KEYVAULT_URL"],
        credential=credential
    )

    password = secret_client.get_secret(
        os.environ["POSTGRES_PASSWORD_SECRET"]
    ).value

    conn_str = (
        f"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{password}"
        f"@{os.environ['POSTGRES_HOST']}:5432/{os.environ['POSTGRES_DB']}"
        f"?sslmode={os.environ['POSTGRES_SSLMODE']}"
    )

    return create_engine(conn_str, pool_pre_ping=True)


# 
# SQLAlchemy table metadata (MATCHES PostgreSQL DB)

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

# FINAL weather_condition schema:

weather_condition = Table(
    "weather_condition", metadata,
    Column("weather_condition_id", BigInteger, primary_key=True),
    Column("external_condition_id", Integer),
    Column("main", Text),
    Column("description", Text),
    Column("icon", Text),
)

# weather_reading schema:

weather_reading = Table(
    "weather_reading", metadata,
    Column("weather_reading_id", BigInteger, primary_key=True),
    Column("event_time", TIMESTAMP(timezone=True)),
    Column("location_id", BigInteger),
    Column("weather_condition_id", BigInteger),
    Column("temperature", DECIMAL(5, 2)),
    Column("feels_like", DECIMAL(5, 2)),
    Column("pressure", Integer),
    Column("humidity", Integer),
    Column("wind_speed", DECIMAL(5, 2)),
    Column("wind_deg", Integer),
    Column("visibility", Integer),
    Column("cloudiness", Integer),
)

# IoT schema 
iot_reading = Table(
    "iot_reading", metadata,
    Column("iot_reading_id", BigInteger, primary_key=True),
    Column("event_time", TIMESTAMP(timezone=True)),
    Column("location_id", BigInteger),
    Column("temperature", DECIMAL(5, 2)),
    Column("humidity", DECIMAL(5, 2)),
    Column("water_level", DECIMAL(5, 2)),
    Column("nitrogen", DECIMAL(5, 2)),
    Column("phosphorus", DECIMAL(5, 2)),
    Column("potassium", DECIMAL(5, 2)),
)



# Event Hub trigger: Event Hub -> Postgres

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
        logging.exception("Failed to decode Event Hub message as JSON")
        return

    event_type = payload.get("event_type")
    engine = get_engine()

    try:
        with engine.begin() as conn:  # one event = one transaction
            if event_type == "weather":
                handle_weather(payload, conn)
            elif event_type == "iot":
                handle_iot(payload, conn)
            else:
                logging.warning(f"Unknown event type: {event_type}")
    except Exception:
        logging.exception("Failed processing event into Postgres")



# Weather ingestion 

def handle_weather(event, conn):
    data = event["payload"]
    event_time = datetime.fromtimestamp(data["dt"], tz=timezone.utc)

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
        .on_conflict_do_update(
            index_elements=["city_name", "country_code"],
            set_={
                "latitude": data["coord"]["lat"],
                "longitude": data["coord"]["lon"],
            }
        )
        .returning(location.c.location_id)
    )
    location_id = conn.execute(loc_stmt).scalar()

    #  Weather condition UPSERT (surrogate PK)
    w = data["weather"][0]

    cond_insert = (
        pg_insert(weather_condition)
        .values(
            external_condition_id=w["id"],
            main=w.get("main"),
            description=w.get("description"),
            icon=w.get("icon"),
        )
        # Unique index in DB external_condition_id, icon
        .on_conflict_do_nothing(
            index_elements=["external_condition_id", "icon"]
        )
        .returning(weather_condition.c.weather_condition_id)
    )

    weather_condition_id = conn.execute(cond_insert).scalar()

    # If it already existed, fetch the surrogate key
    if weather_condition_id is None:
        weather_condition_id = conn.execute(
            select(weather_condition.c.weather_condition_id).where(
                (weather_condition.c.external_condition_id == w["id"]) &
                (weather_condition.c.icon == w.get("icon"))
            )
        ).scalar_one()

    #  Weather reading INSERT 
    conn.execute(
        pg_insert(weather_reading)
        .values(
            event_time=event_time,
            location_id=location_id,
            weather_condition_id=weather_condition_id,
            temperature=data["main"].get("temp"),
            feels_like=data["main"].get("feels_like"),
            pressure=data["main"].get("pressure"),
            humidity=data["main"].get("humidity"),
            wind_speed=data.get("wind", {}).get("speed"),
            wind_deg=data.get("wind", {}).get("deg"),
            visibility=data.get("visibility"),
            cloudiness=data.get("clouds", {}).get("all"),
        )
        .on_conflict_do_nothing()
    )



# IoT ingestion 

def handle_iot(event, conn):
    data = event["payload"]

    
    event_time = datetime.fromisoformat(data["measurement_time"])

    
    location_id = None

    conn.execute(
        pg_insert(iot_reading)
        .values(
            event_time=event_time,
            location_id=location_id,
            temperature=data.get("temperature"),
            humidity=data.get("humidity"),
            water_level=data.get("water_level"),
            nitrogen=data.get("nitrogen"),
            phosphorus=data.get("phosphorus"),
            potassium=data.get("potassium"),
        )
        .on_conflict_do_nothing()
    )

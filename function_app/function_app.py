import logging
import hashlib
import azure.functions as func
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import json
from datetime import datetime, timezone

app = func.FunctionApp()

@app.function_name(name="fetchweatherapi")
@app.timer_trigger(
    schedule="0 * * * * *",
    arg_name="myTimer",
    run_on_startup=False
)
# push data to even hub
@app.event_hub_output(arg_name="eventhub",event_hub_name="streaming_iot_time_series",connection="EVENT_HUB_CONNECTION")


def fetchweatherapi(myTimer: func.TimerRequest,eventhub: func.Out[str]) -> None:
    if myTimer.past_due:
        logging.info("The timer is past due!")
        
    KEYVAULT_URL = "https://kv-Az-TimeSeries.vault.azure.net/"

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    #API_KEY = ""  
    city = "windhoek"  

    try:
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=KEYVAULT_URL, credential=credential)
        api_key_secret = secret_client.get_secret("weather-api-key")
        API_KEY = api_key_secret.value

        response = requests.get(BASE_URL, params={"appid": API_KEY, "q": city})
        response.raise_for_status()
        data = response.json()
        # unique identifier
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
        #send to evenhub
        eventhub.set(json.dumps(event))

        logging.info(f"Weather data for {city}: {data} and this have been send to even_hub as well")
    except Exception as e:
        logging.error(f"Error fetching weather data: {e}")
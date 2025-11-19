import logging
import azure.functions as func
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = func.FunctionApp()


@app.schedule(
    schedule="0 * * * * *",
    arg_name="myTimer",
    run_on_startup=True,
    use_monitor=False
)
def fetchweatherapi(myTimer: func.TimerRequest) -> None:
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
        logging.info(f"Weather data for {city}: {data}")
    except Exception as e:
        logging.error(f"Error fetching weather data: {e}")
        
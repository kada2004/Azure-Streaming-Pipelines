from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import json
import linecache
import requests
import time


# CONFIG

KEYVAULT_URL = "https://kv-Az-TimeSeries.vault.azure.net/"
SECRET_NAME = "apim-subscription-key"
API_URL = "https://apim-az-management.azure-api.net/ingest"

#SUBSCRIPTION_KEY = ""

# Authenticate
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KEYVAULT_URL, credential=credential)

# Get secret
SUBSCRIPTION_KEY = client.get_secret(SECRET_NAME).value
INPUT_FILE = "./output10lines.txt"

START_LINE = 1
END_LINE = 10

HEADERS = {
    "Content-Type": "application/json",
    "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY
}


# SEND LOOP

for i in range(START_LINE, END_LINE + 1):
    line = linecache.getline(INPUT_FILE, i)

    if not line.strip():
        print(f"Line {i} is empty, skipping")
        continue

    try:
        payload = json.loads(line)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON at line {i}: {e}")
        continue

    print(f"Sending line {i}: {payload}")

    response = requests.post(
        API_URL,
        headers=HEADERS,
        json=payload,
        timeout=10
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    
    time.sleep(0.05)

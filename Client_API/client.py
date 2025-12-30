from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import json
import linecache
import requests
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone


# Config

KEYVAULT_URL = "https://kv-Az-TimeSeries.vault.azure.net/"
SECRET_NAME = "apim-subscription-key"
API_URL = "https://apim-az-management.azure-api.net/ingest"

INPUT_FILE = "./output10lines.txt"
START_LINE = 1
END_LINE = 10

# AUTH


credential = DefaultAzureCredential()
client = SecretClient(vault_url=KEYVAULT_URL, credential=credential)
SUBSCRIPTION_KEY = client.get_secret(SECRET_NAME).value

HEADERS = {
    "Content-Type": "application/json",
    "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY
}

file_name = Path(INPUT_FILE).name


for line_number in range(START_LINE, END_LINE + 1):

    line = linecache.getline(INPUT_FILE, line_number)

    if not line.strip():
        print(f"Line {line_number} is empty, skipping")
        continue

    try:
        payload = json.loads(line)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON at line {line_number}: {e}")
        continue

    # stable JSON 
    canonical_payload = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":")
    )

    # event_time
    event_time = payload.get(
        "event_time",
        datetime.now(timezone.utc).isoformat()
    )

    # event_id 
    raw_id = f"{file_name}|line={line_number}|{canonical_payload}"
    event_id = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()

    #  message 
    message = {
        "event_id": event_id,
        "event_time": event_time,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "source_file": file_name,
        "source_line": line_number,
        "payload": payload
    }

    print(f"Sending line {line_number} | event_id={event_id}")

    response = requests.post(
        API_URL,
        headers=HEADERS,
        json=message,
        timeout=10
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    time.sleep(0.05)

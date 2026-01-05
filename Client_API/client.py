from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import json
import linecache
import requests
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone



# CONFIG TO GET SECRETS FROM KEYVAULT

KEYVAULT_URL = "https://kv-Az-TimeSeries.vault.azure.net/"
SECRET_NAME = "apim-subscription-key"
API_URL = "https://apim-az-management.azure-api.net/ingest"

INPUT_FILE = "./output10lines.txt"
START_LINE = 1
END_LINE = 10



# AUTH to my API 


credential = DefaultAzureCredential()
client = SecretClient(vault_url=KEYVAULT_URL, credential=credential)
SUBSCRIPTION_KEY = client.get_secret(SECRET_NAME).value

HEADERS = {
    "Content-Type": "application/json",
    "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY
}

file_name = Path(INPUT_FILE).name


# Parse Json

def parse_iot_json_line(line: str) -> dict:
   

    record = json.loads(line)

    # Extract the CSV value 
    csv_value = next(iter(record.values()))

    parts = csv_value.strip().split(",")

    if len(parts) < 13:
        raise ValueError("Invalid IoT CSV payload")

    return {
        "measurement_time": parts[0],
        "temperature": int(parts[1]),
        "humidity": int(parts[2]),
        "water_level": int(parts[3]),
        "nitrogen": int(parts[4]),
        "phosphorus": int(parts[5]),
        "potassium": int(parts[6]),
        "fan_actuator_off": int(float(parts[7])),
        "fan_actuator_on": int(float(parts[8])),
        "watering_pump_off": int(float(parts[9])),
        "watering_pump_on": int(float(parts[10])),
        "water_pump_off": int(float(parts[11])),
        "water_pump_on": int(float(parts[12]))
    }


def generate_event_id(file_name: str, line_number: int, payload: dict) -> str:
    """
    Generates a  event_id 
    """
    canonical_payload = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":")
    )

    raw_id = f"{file_name}|line={line_number}|{canonical_payload}"
    return hashlib.sha256(raw_id.encode("utf-8")).hexdigest()


# Loop to send json data

for line_number in range(START_LINE, END_LINE + 1):

    line = linecache.getline(INPUT_FILE, line_number)

    if not line.strip():
        print(f"Line {line_number} is empty skipping")
        continue

    try:
        payload = parse_iot_json_line(line)
    except Exception as e:
        print(f"Failed to parse line {line_number}: {e}")
        continue

    event_time = payload.get(
        "measurement_time",
        datetime.now(timezone.utc).isoformat()
    )

    event_id = generate_event_id(file_name, line_number, payload)

    message = {
        "event_id": event_id,
        "event_type": "iot",
        "event_time": event_time,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "source_file": file_name,
        "source_line": line_number,
        "payload": payload
    }

    print(f"Sending line {line_number} | event_id={event_id}")

    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json=message,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed for line {line_number}: {e}")

    time.sleep(0.05)

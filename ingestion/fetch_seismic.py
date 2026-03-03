import os
import sys
import json
import requests
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import storage
from config.gcp_config import (
    PROJECT_ID,
    GCS_BUCKET_NAME,
    RAW_DATA_PATH,
    USGS_API_URL
)

def fetch_seismic_data():
    response = requests.get(USGS_API_URL)
    response.raise_for_status()
    return response.json()

def save_to_gcs(data):
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(GCS_BUCKET_NAME)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{RAW_DATA_PATH}seismic_{timestamp}.json"
    
    blob = bucket.blob(filename)
    blob.upload_from_string(
        json.dumps(data),
        content_type="application/json"
    )
    print(f"Saved: {filename}")
    return filename

def run():
    print("Fetching seismic data...")
    data = fetch_seismic_data()
    
    total = len(data["features"])
    print(f"Earthquakes fetched: {total}")
    
    filename = save_to_gcs(data)
    print(f"Done! File saved to GCS: {filename}")

if __name__ == "__main__":
    run()
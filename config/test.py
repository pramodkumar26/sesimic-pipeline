import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/service-account-key.json"

from google.cloud import storage
from config.gcp_config import PROJECT_ID, GCS_BUCKET_NAME

def test_gcs_connection():
    try:
        client = storage.Client(project=PROJECT_ID)
        bucket = client.get_bucket(GCS_BUCKET_NAME)
        print("Connection Successful!")
        print(f"Bucket found: {bucket.name}")
        print(f"Location: {bucket.location}")
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    test_gcs_connection()
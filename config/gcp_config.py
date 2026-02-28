import os
from dotenv import load_dotenv

load_dotenv()

# GCP Project
PROJECT_ID = os.getenv("PROJECT_ID", "sesimic-pipeline")
REGION = os.getenv("REGION", "us-central1")

# GCS
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "sesimic-pipeline-raw-data")
RAW_DATA_PATH = "raw/seismic/"

# Pub/Sub
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "seismic-events")
PUBSUB_SUBSCRIPTION = os.getenv("PUBSUB_SUBSCRIPTION", "seismic-events-sub")

# Cloud SQL
DB_INSTANCE = os.getenv("DB_INSTANCE", "sesimic-pipeline:us-central1:seismic-db")
DB_NAME = os.getenv("DB_NAME", "seismic_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Service Account
SERVICE_ACCOUNT_KEY = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", 
                                "config/service-account-key.json")

# USGS API
USGS_API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
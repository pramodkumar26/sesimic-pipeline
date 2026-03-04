# Seismic Data Real-Time Pipeline

I built this project to create a fully automated pipeline that tracks earthquakes happening around the world in real time. Every 15 minutes, the pipeline wakes up, fetches the latest earthquake data from the USGS API, streams it through Google Pub/Sub, processes it with PySpark, stores it in a PostgreSQL database, and serves it through a live REST API — all without any manual intervention.

## What It Does

The USGS publishes earthquake data publicly every few minutes. This pipeline taps into that feed automatically, processes the raw data, and makes it queryable through a clean API. You can ask it things like "what earthquakes happened in the last 24 hours?" or "show me all earthquakes above magnitude 4.0" and get a live JSON response.

## Architecture
```
USGS API → Pub/Sub → PySpark on Dataproc → Cloud SQL PostgreSQL → Flask API on Cloud Run
                                                    ↑
                                        Airflow on Compute Engine VM
```

## How the Pipeline Works

Every 15 minutes, an Airflow DAG running on a GCP VM kicks off the following sequence:

1. Fetches the latest earthquake events from the USGS GeoJSON API
2. Publishes each earthquake as a message to a Google Pub/Sub topic
3. Spins up an ephemeral Dataproc cluster, runs a PySpark job that pulls all messages, transforms the data, and writes it as Parquet files to GCS
4. Runs a second PySpark job that loads the Parquet data into a staging table in Cloud SQL
5. Merges the staging data into the main seismic_events table using ON CONFLICT DO NOTHING to avoid duplicates
6. Deletes the Dataproc cluster to keep costs minimal

## Live API

**Base URL:** https://seismic-flask-api-896514553550.us-central1.run.app

| Endpoint | What it returns |
|---|---|
| `/` | API health check |
| `/earthquakes` | Last 100 earthquake events |
| `/earthquakes/recent` | All earthquakes in the last 24 hours |
| `/earthquakes/strong` | All earthquakes with magnitude 4.0 or above |
| `/earthquakes/stats` | Total count, average magnitude, max/min magnitude |

## Tech Stack

| Layer | Technology |
|---|---|
| Data Source | USGS Earthquake GeoJSON API |
| Messaging | Google Pub/Sub |
| Processing | PySpark on Google Dataproc |
| Storage | Cloud SQL PostgreSQL + GCS (Parquet) |
| Orchestration | Apache Airflow on Compute Engine VM |
| API | Flask deployed on Cloud Run |
| Language | Python 3.10 |
| Cloud | GCP |

## Project Structure
```
seismic-pipeline/
├── ingestion/
│   └── fetch_seismic.py        # Pulls earthquake data from USGS API and saves to GCS
├── streaming/
│   ├── producer.py             # Publishes earthquake events to Pub/Sub
│   └── consumer.py             # Pulls from Pub/Sub, processes with PySpark, writes Parquet to GCS
├── database/
│   ├── schema.sql              # PostgreSQL table definitions
│   ├── db_loader.py            # Loads Parquet from GCS into Cloud SQL staging table
│   └── merge_staging.py        # Merges staging data into main table without duplicates
├── dags/
│   └── seismic_dag.py          # Airflow DAG that orchestrates the full pipeline
└── flask_app/
    ├── app.py                  # Flask REST API with earthquake query endpoints
    ├── Dockerfile              # Container definition for Cloud Run deployment
    └── requirements.txt        
```

## Key Engineering Decisions

**Ephemeral Dataproc clusters** — The pipeline creates a Dataproc cluster at the start of each run and deletes it when done. This keeps GCP credit usage minimal since Dataproc is the only expensive component.

**Staging table pattern** — Instead of inserting directly into the main table, data first lands in a staging table and is then merged using `ON CONFLICT DO NOTHING`. This prevents duplicate key errors when the same earthquake appears across multiple pipeline runs.

**Parquet on GCS as data lake** — Raw processed data accumulates in GCS as Parquet files, giving a full historical record independent of the database.

**Airflow on Compute Engine instead of Cloud Composer** 
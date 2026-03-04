from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import subprocess
import sys
import os

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}


def fetch_and_publish():
    sys.path.insert(0, '/home/pramodarun26/seismic-pipeline')
    from ingestion.fetch_seismic import run as fetch_run
    from streaming.producer import publish_messages
    fetch_run()
    publish_messages()
    print("Fetch and publish completed")

with DAG(
    dag_id='seismic_pipeline',
    default_args=default_args,
    description='Seismic data pipeline',
    schedule_interval='*/15 * * * *',
    start_date=datetime(2026, 3, 1),
    catchup=False,
) as dag:

    task_fetch_publish = PythonOperator(
        task_id='fetch_and_publish',
        python_callable=fetch_and_publish,
    )

    task_create_cluster = BashOperator(
        task_id='create_dataproc_cluster',
        bash_command='''
        gcloud dataproc clusters create seismic-cluster \
            --region=us-central1 \
            --zone=us-central1-a \
            --master-machine-type=e2-standard-2 \
            --master-boot-disk-size=30 \
            --num-workers=2 \
            --worker-machine-type=e2-standard-2 \ 
            --worker-boot-disk-size=30\
	    --single-node
        ''',
    )

    task_run_consumer = BashOperator(
        task_id='run_consumer',
        bash_command='''
        gcloud dataproc jobs submit pyspark \
            gs://sesimic-pipeline-raw-data/scripts/consumer.py \
            --cluster=seismic-cluster \
            --region=us-central1
        ''',
    )

    task_run_db_loader = BashOperator(
        task_id='run_db_loader',
        bash_command='''
        gcloud dataproc jobs submit pyspark \
            gs://sesimic-pipeline-raw-data/scripts/db_loader.py \
            --cluster=seismic-cluster \
            --region=us-central1 \
            --jars=gs://sesimic-pipeline-raw-data/jars/postgresql-42.7.3.jar
        ''',
    )

    task_delete_cluster = BashOperator(
        task_id='delete_dataproc_cluster',
        bash_command='''
        gcloud dataproc clusters delete seismic-cluster \
            --region=us-central1 \
            --quiet
        ''',
    )

    task_fetch_publish >> task_create_cluster >> task_run_consumer >> task_run_db_loader >> task_delete_cluster

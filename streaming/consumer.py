import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import pubsub_v1
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType
from pyspark.sql.functions import to_timestamp, col

PROJECT_ID = "sesimic-pipeline"
SUBSCRIPTION = "projects/sesimic-pipeline/subscriptions/seismic-events-sub"
GCS_BUCKET = "sesimic-pipeline-raw-data"

schema = StructType([
    StructField("id", StringType()),
    StructField("magnitude", DoubleType()),
    StructField("place", StringType()),
    StructField("time", LongType()),
    StructField("longitude", DoubleType()),
    StructField("latitude", DoubleType()),
    StructField("depth", DoubleType())
])

def pull_messages():
    subscriber = pubsub_v1.SubscriberClient()
    messages = []

    response = subscriber.pull(
        request={
            "subscription": SUBSCRIPTION,
            "max_messages": 100
        }
    )

    ack_ids = []
    for msg in response.received_messages:
        data = json.loads(msg.message.data.decode("utf-8"))
        messages.append(data)
        ack_ids.append(msg.ack_id)

    if ack_ids:
        subscriber.acknowledge(
            request={
                "subscription": SUBSCRIPTION,
                "ack_ids": ack_ids
            }
        )

    print(f"Pulled {len(messages)} messages from Pub/Sub")
    return messages

def process_with_spark(messages):
    spark = SparkSession.builder \
        .appName("SeismicConsumer") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    cleaned = []
    for m in messages:
        cleaned.append({
            "id": str(m["id"]),
            "magnitude": float(m["magnitude"]),
            "place": str(m["place"]),
            "time": int(m["time"]),
            "longitude": float(m["longitude"]),
            "latitude": float(m["latitude"]),
            "depth": float(m["depth"])
        })

    df = spark.createDataFrame(cleaned, schema=schema)

    df = df.withColumn(
        "event_time",
        to_timestamp(col("time") / 1000)
    )

    df.show(truncate=False)

    output_path = f"gs://{GCS_BUCKET}/processed/seismic/"
    df.write.mode("append").parquet(output_path)
    print(f"Saved {df.count()} records to {output_path}")

def run():
    messages = pull_messages()
    if not messages:
        print("No messages found in Pub/Sub")
        return
    process_with_spark(messages)
    print("Job completed!")

if __name__ == "__main__":
    run()
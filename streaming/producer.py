import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import pubsub_v1
from config.gcp_config import PROJECT_ID, PUBSUB_TOPIC
from ingestion.fetch_seismic import fetch_seismic_data

def publish_messages():
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)

    data = fetch_seismic_data()
    earthquakes = data["features"]

    print(f"Publishing {len(earthquakes)} earthquake events...")

    for quake in earthquakes:
        properties = quake["properties"]
        coordinates = quake["geometry"]["coordinates"]

        message = {
            "id": quake["id"],
            "magnitude": properties["mag"],
            "place": properties["place"],
            "time": properties["time"],
            "longitude": coordinates[0],
            "latitude": coordinates[1],
            "depth": coordinates[2]
        }

        message_bytes = json.dumps(message).encode("utf-8")
        future = publisher.publish(topic_path, message_bytes)
        future.result()

    print(f"Done! {len(earthquakes)} messages published to {PUBSUB_TOPIC}")

if __name__ == "__main__":
    publish_messages()
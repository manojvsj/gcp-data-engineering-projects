#!/usr/bin/env python3
"""
Simple Streaming Pipeline for Beginners
Read from Pub/Sub -> Write to BigQuery
"""

import json
import logging
import yaml

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions
from apache_beam.io.gcp.pubsub import ReadFromPubSub
from apache_beam.io.gcp.bigquery import WriteToBigQuery, BigQueryDisposition


def load_config():
    """Load configuration from config.yaml"""
    with open("../config/config.yaml", "r") as file:
        return yaml.safe_load(file)


def parse_message(element):
    """Parse JSON message from Pub/Sub"""
    import datetime
    try:
        # Decode the message
        message = json.loads(element.decode("utf-8"))

        # Add processing timestamp using timezone-aware datetime
        message["processing_timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')

        # Extract properties for flat BigQuery schema
        properties = message.get("properties", {})

        # Create flat record for BigQuery
        flat_record = {
            "event_id": message.get("event_id"),
            "event_type": message.get("event_type"),
            "user_id": message.get("user_id"),
            "session_id": message.get("session_id"),
            "event_timestamp": message.get("event_timestamp"),
            "processing_timestamp": message.get("processing_timestamp"),
            "data_source": message.get("data_source"),
            "schema_version": message.get("schema_version"),
            # Product info from properties
            "product": properties.get("product"),
            "price": properties.get("price"),
            "quantity": properties.get("quantity", 1),
            "country": properties.get("country"),
            "device_type": properties.get("device_type"),
            "page_url": properties.get("page_url"),
            "referrer": properties.get("referrer"),
        }

        print(
            f"✅ Processed event: {flat_record['event_id']} - {flat_record['event_type']}"
        )
        return flat_record

    except Exception as e:
        logging.error(f"Failed to parse message: {element}, Error: {e}")
        print(f"Failed to parse message: {element}, Error: {e}")
        return None




class WriteToGCS(beam.DoFn):
    """Write each event to individual GCS file"""

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def process(self, element):
        """Write single event to GCS file"""
        from google.cloud import storage
        import datetime
        import uuid

        try:
            # Create filename with date path structure
            now = datetime.datetime.now()
            date_path = now.strftime("%Y-%m-%d")
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"iceberg-staging/events/{date_path}/{timestamp}_{unique_id}.json"

            # Write to GCS
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(filename)
            blob.upload_from_string(element)

            print(f"✅ Event written: {filename}")

        except Exception as e:
            print(f"❌ GCS write failed: {e}")


def run_simple_pipeline():
    """Run a simple streaming pipeline"""

    # Load config for topic and table names
    config = load_config()

    print(f" Reading from: {config['pubsub']['input_topic']}")
    print(
        f"📊 Writing to: {config['bigquery']['dataset']}.{config['bigquery']['realtime_table']}"
    )
    print()

    # Apache Beam automatically parses command line arguments!
    # No need for argparse - just call PipelineOptions() with no arguments
    pipeline_options = PipelineOptions()

    # BigQuery schema matching the publisher data
    schema = (
        "event_id:STRING,"
        "event_type:STRING,"
        "user_id:STRING,"
        "session_id:STRING,"
        "event_timestamp:TIMESTAMP,"
        "processing_timestamp:TIMESTAMP,"
        "data_source:STRING,"
        "schema_version:STRING,"
        "product:STRING,"
        "price:FLOAT,"
        "quantity:INTEGER,"
        "country:STRING,"
        "device_type:STRING,"
        "page_url:STRING,"
        "referrer:STRING"
    )

    # Get the project from pipeline options for the table reference
    google_cloud_options = pipeline_options.view_as(GoogleCloudOptions)
    project_id = google_cloud_options.project

    # Create and run pipeline
    with beam.Pipeline(options=pipeline_options) as pipeline:

        # Read and parse messages
        parsed_messages = (
            pipeline
            | "Read from Pub/Sub"
            >> ReadFromPubSub(topic=config["pubsub"]["input_topic"])
            | "Parse Messages" >> beam.Map(parse_message)
            | "Filter Valid" >> beam.Filter(lambda x: x is not None)
        )

        # Write to BigQuery (simple streaming inserts)
        (
            parsed_messages
            | "Write to BigQuery"
            >> WriteToBigQuery(
                table=f"{project_id}:{config['bigquery']['dataset']}.{config['bigquery']['realtime_table']}",
                schema=schema,
                write_disposition=BigQueryDisposition.WRITE_APPEND,
                create_disposition=BigQueryDisposition.CREATE_IF_NEEDED
            )
        )

        # Write to GCS - individual file per event (simple)
        (
            parsed_messages
            | "Convert to JSON" >> beam.Map(lambda x: json.dumps(x))
            | "Write to GCS" >> beam.ParDo(WriteToGCS(config.get('gcs', {}).get('temp_bucket', 'dataflow-temp-stream001')))
        )

    print("✅ Pipeline submitted successfully!")
    print("📊 Real-time data flowing to BigQuery")
    print("📂 Individual event files written to GCS")
    print("🔄 Run Spark batch job to process GCS files into Iceberg")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    try:
        run_simple_pipeline()
    except Exception as e:
        print(f"❌ Error: {e}")


import base64
import json
import os
from google.cloud import bigquery

def gcs_to_bigquery(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
        event (dict): Event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """
    file = event
    bucket = file['bucket']
    name = file['name']

    print(f"Processing file: gs://{bucket}/{name}")

    project_id = os.environ.get("GCP_PROJECT")
    dataset_id = os.environ.get("BQ_DATASET")
    table_id = os.environ.get("BQ_TABLE")

    uri = f"gs://{bucket}/{name}"
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    client = bigquery.Client()

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
    )

    load_job = client.load_table_from_uri(uri, table_ref, job_config=job_config)
    load_job.result()  # Waits for the job to complete.

    print(f"Loaded {uri} into {table_ref}")
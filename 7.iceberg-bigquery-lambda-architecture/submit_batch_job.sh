#!/bin/bash

# ---- CONFIGURATION ----
PROJECT_ID="<your-project-id>"
UNIQUE_KEY='stream001'
REGION="europe-west2"
NETWORK="default"

# Resource names
GCS_BUCKET_ICEBERG="iceberg-streaming-$UNIQUE_KEY"
GCS_BUCKET_DATAFLOW="dataflow-temp-$UNIQUE_KEY"
PUBSUB_TOPIC="raw-data-stream"
PUBSUB_DLQ_TOPIC="dlq-stream"
PUBSUB_SUBSCRIPTION="dataflow-subscription"
METASTORE_NAME="iceberg-streaming-metastore"
BIGQUERY_DATASET="streaming_analytics"

# Iceberg configuration
ICEBERG_DATABASE="streaming_db"
ICEBERG_TABLE="events"
ICEBERG_WAREHOUSE_PATH="gs://$GCS_BUCKET_ICEBERG/warehouse"
SERVERLESS_JOB_NAME="iceberg-setup-job"


echo "Fetching Metastore URI..."
METASTORE_URI=$(gcloud metastore services describe $METASTORE_NAME \
    --location=$REGION \
    --project=$PROJECT_ID \
    --format="value(endpointUri)")

echo "Metastore URI: $METASTORE_URI"

gsutil cp spark_jobs/gcs_to_iceberg_batch.py gs://$GCS_BUCKET_ICEBERG/scripts/
gsutil cp spark_jobs/batch_analysis.py gs://$GCS_BUCKET_ICEBERG/scripts/
gsutil cp config/config.yaml gs://$GCS_BUCKET_ICEBERG/scripts/
echo "✅ Spark scripts uploaded to gs://$GCS_BUCKET_ICEBERG/scripts/"

# Default to today's date if not provided
TARGET_DATE=${1:-$(date +%Y-%m-%d)}

STEP 1: Load GCS data to Iceberg
BATCH_ID_LOAD="gcs-to-iceberg-$(date +%Y%m%d-%H%M%S)"
echo "🚀 STEP 1: Loading GCS data to Iceberg for $TARGET_DATE"
echo "Submitting GCS to Iceberg batch job: $BATCH_ID_LOAD"
gcloud dataproc batches submit pyspark gs://$GCS_BUCKET_ICEBERG/scripts/gcs_to_iceberg_batch.py \
    --project=$PROJECT_ID \
    --region=$REGION \
    --batch=$BATCH_ID_LOAD \
    --version=2.3 \
    --jars=gs://$GCS_BUCKET_ICEBERG/jars/iceberg-spark-runtime-3.5_2.13-1.9.2.jar \
    --properties=spark.hadoop.hive.metastore.uris=$METASTORE_URI \
    --deps-bucket=$GCS_BUCKET_ICEBERG \
    -- \
    gs://$GCS_BUCKET_ICEBERG/scripts/config.yaml $TARGET_DATE

if [ $? -ne 0 ]; then
    echo "❌ GCS to Iceberg load job failed"
    exit 1
fi

echo "✅ Step 1 completed: Data loaded to Iceberg"

# STEP 2: Run batch analysis
BATCH_ID_ANALYSIS="iceberg-batch-analysis-$(date +%s)"
echo "📊 STEP 2: Running Batch Analysis"
echo "Submitting analysis batch job: $BATCH_ID_ANALYSIS"
gcloud dataproc batches submit pyspark gs://$GCS_BUCKET_ICEBERG/scripts/batch_analysis.py \
    --project=$PROJECT_ID \
    --region=$REGION \
    --batch=$BATCH_ID_ANALYSIS \
    --version=2.3 \
    --jars=gs://$GCS_BUCKET_ICEBERG/jars/iceberg-spark-runtime-3.5_2.13-1.9.2.jar \
    --properties=spark.hadoop.hive.metastore.uris=$METASTORE_URI \
    --deps-bucket=$GCS_BUCKET_ICEBERG \
    -- \
    gs://$GCS_BUCKET_ICEBERG/warehouse $ICEBERG_DATABASE $ICEBERG_TABLE
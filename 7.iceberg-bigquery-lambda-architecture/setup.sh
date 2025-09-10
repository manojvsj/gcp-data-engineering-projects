#!/bin/bash

# ---- CONFIGURATION ----
PROJECT_ID="your-project-id"
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

echo "=== GCP Real-time Streaming Pipeline Setup ==="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Unique Key: $UNIQUE_KEY"

# ---- ENABLE REQUIRED SERVICES ----
echo "Enabling required GCP APIs..."
gcloud services enable \
    dataflow.googleapis.com \
    pubsub.googleapis.com \
    dataproc.googleapis.com \
    metastore.googleapis.com \
    storage.googleapis.com \
    bigquery.googleapis.com

# ---- CREATE BUCKETS ----
echo "Creating GCS buckets..."
gsutil mb -p $PROJECT_ID -l $REGION -c STANDARD gs://$GCS_BUCKET_ICEBERG/
gsutil mb -p $PROJECT_ID -l $REGION -c STANDARD gs://$GCS_BUCKET_DATAFLOW/

# Create bucket structure for Iceberg
gsutil mkdir gs://$GCS_BUCKET_ICEBERG/warehouse
gsutil mkdir gs://$GCS_BUCKET_ICEBERG/scripts
echo "Bucket structure created"

# ---- UPLOAD SPARK SCRIPTS ----
echo "Uploading Spark scripts to GCS..."
if [ ! -f "spark_jobs/iceberg_setup.py" ]; then
    echo "❌ Error: iceberg_setup.py file not found in spark_jobs/ directory"
    echo "Please ensure iceberg_setup.py is in the spark_jobs/ folder"
    exit 1
fi

gsutil cp spark_jobs/iceberg_setup.py gs://$GCS_BUCKET_ICEBERG/scripts/
gsutil cp spark_jobs/gcs_to_iceberg_batch.py gs://$GCS_BUCKET_ICEBERG/scripts/
gsutil cp config/config.yaml gs://$GCS_BUCKET_ICEBERG/scripts/
echo "✅ Spark scripts uploaded to gs://$GCS_BUCKET_ICEBERG/scripts/"

gsutil cp -n jars/iceberg-spark-runtime-3.5_2.13-1.9.2.jar gs://$GCS_BUCKET_ICEBERG/jars/
echo "✅ Iceberg runtime JAR uploaded to gs://$GCS_BUCKET_ICEBERG/jars/"

# ---- CREATE PUB/SUB TOPICS ----
echo "Creating Pub/Sub topics and subscriptions..."
gcloud pubsub topics create $PUBSUB_TOPIC --project=$PROJECT_ID
gcloud pubsub topics create $PUBSUB_DLQ_TOPIC --project=$PROJECT_ID
gcloud pubsub subscriptions create $PUBSUB_SUBSCRIPTION --topic=$PUBSUB_TOPIC --project=$PROJECT_ID

# ---- CREATE BIGQUERY DATASET ----
echo "Creating BigQuery dataset..."
bq --location=$REGION mk -d --description "Streaming analytics dataset" $PROJECT_ID:$BIGQUERY_DATASET

# Create Biglake connections
bq mk --connection --connection_type=CLOUD_RESOURCE \
    --location=$REGION \
    --project_id=$PROJECT_ID \
    --description="Biglake GCS connection for streaming" \
    biglake_streaming_connection

# ---- CREATE DATAPROC METASTORE ----
echo "Creating Dataproc Metastore..."
gcloud metastore services create $METASTORE_NAME \
  --location=$REGION \
  --network=$NETWORK \
  --tier=DEVELOPER \
  --project=$PROJECT_ID \
  --hive-metastore-configs=version=3.1.2

# Wait for metastore to be ready
echo "Waiting for Metastore to be ready..."

# ---- GET METASTORE URI ----
echo "Fetching Metastore URI..."
METASTORE_URI=$(gcloud metastore services describe $METASTORE_NAME \
    --location=$REGION \
    --project=$PROJECT_ID \
    --format="value(endpointUri)")

echo "Metastore URI: $METASTORE_URI"

# ---- SETUP ICEBERG TABLES USING SERVERLESS SPARK ----
echo "Setting up Iceberg tables using Dataproc Serverless..."

# # Submit serverless Spark job for Iceberg setup
BATCH_ID="iceberg-setup-$(date +%s)"
echo "Submitting serverless Spark job: $BATCH_ID"
gcloud dataproc batches submit pyspark gs://$GCS_BUCKET_ICEBERG/scripts/iceberg_setup.py \
    --project=$PROJECT_ID \
    --region=$REGION \
    --batch=$BATCH_ID \
    --version=2.3 \
    --jars=gs://$GCS_BUCKET_ICEBERG/jars/iceberg-spark-runtime-3.5_2.13-1.9.2.jar \
    --properties spark.hadoop.hive.metastore.uris=$METASTORE_URI \
    -- \
    gs://$GCS_BUCKET_ICEBERG/warehouse \
    $ICEBERG_DATABASE \
    $ICEBERG_TABLE

# ---- START DATAFLOW HYBRID PIPELINE ----
echo "🚀 Hybrid Architecture: Dataflow handles Pub/Sub → BigQuery + GCS"
echo "📊 BigQuery: Real-time analytics"
echo "❄️  Iceberg: Batch processing via Spark"
echo ""
echo "✅ Infrastructure setup complete!"
echo "▶️  Start the pipeline: cd dataflow_jobs && ./run_example.sh"



if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS (Darwin)
  sed -i '' "s/your-gcp-project-id/$PROJECT_ID/g" config/config.yaml
  sed -i '' "s/your-iceberg-warehouse/$GCS_BUCKET_ICEBERG/g" config/config.yaml
  sed -i '' "s/your-temp-bucket/$GCS_BUCKET_DATAFLOW/g" config/config.yaml
  sed -i '' "s/europe-west2/$REGION/g" config/config.yaml
  sed -i '' "s/your-iceberg-database/$ICEBERG_DATABASE/g" config/config.yaml
  sed -i '' "s/your-iceberg-table/$ICEBERG_TABLE/g" config/config.yaml
  sed -i '' "s|your-iceberg-warehouse-path|$ICEBERG_WAREHOUSE_PATH|g" config/config.yaml
  sed -i '' "s/your-iceberg-staging-bucket/$GCS_BUCKET_ICEBERG/g" config/config.yaml
else
  # Linux
  sed -i "s/your-gcp-project-id/$PROJECT_ID/g" config/config.yaml
  sed -i "s/your-iceberg-warehouse/$GCS_BUCKET_ICEBERG/g" config/config.yaml
  sed -i "s/your-temp-bucket/$GCS_BUCKET_DATAFLOW/g" config/config.yaml
  sed -i "s/europe-west2/$REGION/g" config/config.yaml
  sed -i "s/your-iceberg-database/$ICEBERG_DATABASE/g" config/config.yaml
  sed -i "s/your-iceberg-table/$ICEBERG_TABLE/g" config/config.yaml
  sed -i "s|your-iceberg-warehouse-path|$ICEBERG_WAREHOUSE_PATH|g" config/config.yaml
  sed -i "s/your-iceberg-staging-bucket/$GCS_BUCKET_ICEBERG/g" config/config.yaml
fi


echo "✅ Setup complete."

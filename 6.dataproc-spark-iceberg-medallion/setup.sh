#!/bin/bash

# ---- CONFIGURATION ----
PROJECT_ID="your-project-id"
UNIQUE_KEY='adsf'
GCS_BUCKET="gcs-iceberg-$UNIQUE_KEY"
REGION="europe-west2"
METASTORE_NAME="iceberg-metastore"
NETWORK="default"
BIGQUERY_DATASET="sales"


# ---- ENABLE REQUIRED SERVICES ----
echo "Enabling required GCP APIs..."
gcloud services enable \
    dataproc.googleapis.com \
    metastore.googleapis.com \
    storage.googleapis.com

# ---- CREATE BUCKETS ----
echo "Creating GCS buckets for medallion layers..."
gsutil mb -p $PROJECT_ID -l $REGION -c STANDARD gs://$GCS_BUCKET/

# Upload data and script
gsutil cp ./data/input/orders_data.csv gs://$GCS_BUCKET/raw-data/orders/

# ---- CREATE DATA LAKE DIRECTORIES ----
bq --location=${REGION} mk -d --description "External bigquery dataset" ${PROJECT_ID}:${BIGQUERY_DATASET}

# create Biglake connections
bq mk --connection --connection_type=CLOUD_RESOURCE \
    --location=${REGION} \
    --description="Biglake GCS connection" \
    ${PROJECT_ID}:biglake_gcs_connection

# ---- CREATE DATAPROC METASTORE ----
echo "Creating Dataproc Metastore..."
gcloud metastore services create $METASTORE_NAME \
  --location=$REGION \
  --network=$NETWORK \
  --tier=DEVELOPER \
  --hive-metastore-configs=version=3.1.2

# ---- OUTPUT METASTORE URI ----
echo "Fetching Metastore URI..."
METASTORE_URI=$(gcloud metastore services describe $METASTORE_NAME \
    --location=$REGION \
    --format="value(endpointUri)")

echo "Metastore URI: $METASTORE_URI"

# ---- SET PERMISSIONS (OPTIONAL) ----
# echo "Setting IAM roles for Dataproc to access GCS and Metastore..."
# gcloud projects add-iam-policy-binding $PROJECT_ID \
#   --member="serviceAccount:$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')-compute@developer.gserviceaccount.com" \
#   --role="roles/metastore.editor"

echo "✅ Setup complete."

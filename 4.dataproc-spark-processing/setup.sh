#!/bin/bash

# Replace these values
PROJECT_ID="your project id"
REGION="europe-west2"
DATASET="biglake_sales"
TABLE="sales"


UNIQUE_KEY='learning-adsf'
GCS_BUCKET="dataproc-$UNIQUE_KEY"
TEMP_BUCKET="dataproc-temp-$UNIQUE_KEY"
PYSPARK_FILE="pyspark_job.py"
CLUSTER_NAME="gcp-learning-4-cluster" # it need unique name

# Create buckets
gsutil mb -l $REGION gs://$GCS_BUCKET/
gsutil mb -l $REGION gs://$TEMP_BUCKET/

Upload data and script
gsutil cp ./data/input/orders_data.csv gs://$GCS_BUCKET/input/
gsutil cp $PYSPARK_FILE gs://$GCS_BUCKET/scripts/

# Create Dataset if it doesn't exist
if ! bq --location=$REGION ls --format=prettyjson $DATASET >/dev/null 2>&1; then
  echo "Creating dataset $DATASET..."
  bq --location=$REGION mk --dataset $PROJECT_ID:$DATASET
else
  echo "Dataset $DATASET already exists."
fi

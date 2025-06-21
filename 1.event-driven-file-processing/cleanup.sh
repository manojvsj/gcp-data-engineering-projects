#!/bin/bash

# Exit if any command fails
set -e

# CONFIGURATION (update these with your actual values)
PROJECT_ID="your-project-id"
BUCKET_NAME="your-bucket-name"
REGION="us-central1"
FUNCTION_NAME="gcs_to_bigquery"

BQ_DATASET="your_dataset"
BQ_TABLE="your_table"

# Set the project
gcloud config set project $PROJECT_ID

# Delete Cloud Function
echo "Deleting Cloud Function: $FUNCTION_NAME..."
gcloud functions delete $FUNCTION_NAME --region=$REGION --quiet

# Delete BigQuery table
echo "Deleting BigQuery table: $DATASET.$TABLE..."
bq rm -f -t ${PROJECT_ID}:${BQ_DATASET}.${BQ_TABLE}

# Delete GCS bucket
echo "Deleting GCS bucket: gs://$BUCKET_NAME..."
gsutil -m rm -r gs://$BUCKET_NAME
#!/bin/bash

# Exit on any error
# set -e

# CONFIGURATION (replace with your actual values)
PROJECT_ID="your-project-id"
BUCKET_NAME="your-bucket-name"
REGION="us-central1"
FUNCTION_NAME="gcs_to_bigquery"
RUNTIME="python311"

BQ_DATASET="your_dataset"
BQ_TABLE="your_table"


# Authenticate with Google Cloud
# echo "Authenticating with GCP..."
# gcloud auth login

# Set the project
echo "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required services
echo "Enabling required APIs..."
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable bigquery.googleapis.com

# Create GCS bucket if it doesn't exist
if gsutil ls -b gs://$BUCKET_NAME &>/dev/null; then
  echo "Bucket gs://$BUCKET_NAME already exists."
else
  echo "Creating bucket gs://$BUCKET_NAME..."
  gsutil mb -l $REGION gs://$BUCKET_NAME
fi

# Create bigquery dataset and table
echo "Creating BigQuery dataset and table..."
bq --location=$REGION mk --dataset $PROJECT_ID:$BQ_DATASET || echo "Dataset already exists."

bq query --use_legacy_sql=false "
CREATE TABLE IF NOT EXISTS \`$PROJECT_ID.$BQ_DATASET.$BQ_TABLE\` (
  id INT64,
  name STRING,
  email STRING
);"

# Get the project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Construct the GCS service account
GCS_SERVICE_ACCOUNT="service-${PROJECT_NUMBER}@gs-project-accounts.iam.gserviceaccount.com"

# Grant Pub/Sub Publisher role to GCS service account
echo "Granting Pub/Sub Publisher role to $GCS_SERVICE_ACCOUNT..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
--member="serviceAccount:${GCS_SERVICE_ACCOUNT}" \
--role="roles/pubsub.publisher" \
--quiet

# Deploy the Cloud Function
echo "Deploying Cloud Function $FUNCTION_NAME..."
gcloud functions deploy $FUNCTION_NAME \
--runtime $RUNTIME \
--trigger-resource $BUCKET_NAME \
--trigger-event google.storage.object.finalize \
--entry-point gcs_to_bigquery \
--source . \
--region $REGION \
--set-env-vars GCP_PROJECT=$PROJECT_ID,BQ_DATASET=$BQ_DATASET,BQ_TABLE=$BQ_TABLE \
--memory=256MB \
--timeout=60s \
--quiet

echo "✅ Cloud Function deployed successfully!"
#!/bin/bash

# Load .env file if it exists
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Use environment variables or defaults
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-gcp-project-id}"
REGION="${REGION:-us-central1}"
SERVICE_ACCOUNT_NAME="gcp-agent-sa-testing"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Setting project to $PROJECT_ID"
gcloud config set project $PROJECT_ID

echo "Enabling APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com \
    bigquery.googleapis.com storage.googleapis.com aiplatform.googleapis.com

echo "Creating service account..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name="GCP Agent Assistant SA" || echo "Service account exists"

echo "Granting IAM roles..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/bigquery.dataViewer" --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/bigquery.jobUser" --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/storage.objectViewer" --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/aiplatform.user" --quiet

echo "Setup completed!"

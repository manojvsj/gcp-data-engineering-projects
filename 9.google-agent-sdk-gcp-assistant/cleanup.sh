#!/bin/bash

# Load .env file if it exists
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Use environment variables or defaults
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-gcp-project-id}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="gcp-agent-assistant"
SERVICE_ACCOUNT_EMAIL="gcp-agent-sa-testing@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud config set project $PROJECT_ID

echo "Deleting Cloud Run service..."
gcloud run services delete $SERVICE_NAME --region=$REGION --quiet || echo "Service not found"

echo "Deleting service account..."
gcloud iam service-accounts delete $SERVICE_ACCOUNT_EMAIL --quiet || echo "SA not found"

echo "Cleanup completed!"

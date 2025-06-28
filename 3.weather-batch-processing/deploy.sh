#!/bin/bash

# set -e

# CONFIGURE
PROJECT_ID="your project name"
REGION="europe-west1"
FUNCTION_NAME="fetch_weather"
SCHEDULE="*/15 * * * *"
DATASET="weather_dt"
TABLE="weather_snapshots"

# Enable required services
# gcloud services enable cloudfunctions.googleapis.com scheduler.googleapis.com bigquery.googleapis.com


# Create bigquery dataset and table
echo "Creating BigQuery dataset and table..."
bq --location=$REGION mk --dataset $PROJECT_ID:$DATASET || echo "Dataset already exists."

# Create BigQuery table (if not exists)
bq query --use_legacy_sql=false --format=none "
CREATE TABLE IF NOT EXISTS \`${PROJECT_ID}.${DATASET}.${TABLE}\` (
  temperature FLOAT64,
  windspeed FLOAT64,
  recorded_at TIMESTAMP,
  fetched_at TIMESTAMP
);"


# Deploy the function
gcloud functions deploy $FUNCTION_NAME   --region=$REGION   --runtime=python311   --entry-point=fetch_weather   --trigger-http   --allow-unauthenticated   --source=.   --set-env-vars=PROJECT_ID=$PROJECT_ID,DATASET=$DATASET,TABLE=$TABLE

# Get function URL
URL=$(gcloud functions describe $FUNCTION_NAME --region=$REGION --format='value(serviceConfig.uri)')

# Create scheduler job
gcloud scheduler jobs create http weather-scheduler-job \
  --schedule="$SCHEDULE" \
  --http-method=GET \
  --uri=$URL \
  --location=$REGION

echo "✅ Function deployed and scheduler job created."
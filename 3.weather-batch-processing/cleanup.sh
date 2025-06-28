#!/bin/bash
PROJECT_ID="your project name"
REGION="europe-west1"
FUNCTION_NAME="fetch_weather"
DATASET="weather_dt"
TABLE="weather_snapshots"
BUCKET_NAME="weather-code-bucket-abcdf"

# Delete Cloud Function
gcloud functions delete $FUNCTION_NAME --region=$REGION --quiet

# Delete BigQuery table
bq rm -f -t ${PROJECT_ID}:${DATASET}.${TABLE}

# Delete Cloud Scheduler job
gcloud scheduler jobs delete weather-scheduler-job --quiet --location=$REGION

echo "✅ Cleanup complete."
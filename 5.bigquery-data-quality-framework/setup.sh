#!/bin/bash

# Set your project and dataset variables
PROJECT_ID="your project name"
DATASET="data_quality"
FUNCTION_NAME="dq_checker"
REGION=europe-west2
SCHEDULER_NAME="trigger-dq-checks"
SCHEDULE="0 6 * * *" # every day at 6 AM


# Create dataset if not exists
bq --location=EU mk -d --description "Data Quality Monitoring Dataset" ${PROJECT_ID}:${DATASET}

# Create data quality results table
bq query --use_legacy_sql=false "
CREATE TABLE IF NOT EXISTS \`${PROJECT_ID}.${DATASET}.data_quality_results\` (
  partition_date DATE,
  check_name STRING,
  table_name STRING,
  failed_rows INT64,
  total_rows INT64,
  pass_ratio FLOAT64,
  checked_at TIMESTAMP
)"

gcloud functions deploy ${FUNCTION_NAME} \
  --project ${PROJECT_ID} \
  --runtime python311 \
  --trigger-http \
  --entry-point main \
  --source . \
  --region=europe-west2 \
  --memory=512MB \
  --allow-unauthenticated

# Get function URL
URL=$(gcloud functions describe $FUNCTION_NAME --region=$REGION --format="value(serviceConfig.uri)" --project=$PROJECT_ID)

# Create Cloud Scheduler job
gcloud scheduler jobs create http $SCHEDULER_NAME \
  --project=$PROJECT_ID \
  --location=$REGION \
  --schedule="$SCHEDULE" \
  --uri=$URL \
  --http-method=POST \
  --time-zone="Asia/Kolkata"

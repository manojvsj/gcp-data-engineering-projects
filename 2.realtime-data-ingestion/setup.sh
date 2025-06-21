#!/bin/bash

# ---- CONFIG ----
PROJECT_ID="your-project-id"
TOPIC_ID="your-topic-id"
SUBSCRIPTION_ID="your-sub-id"
BQ_DATASET="your_dataset"
BQ_TABLE="your_table"
GCS_BUCKET="your-bucket-name"
REGION="us-central1"


# ---- SETUP ----

echo "Setting project to $PROJECT_ID"
gcloud config set project $PROJECT_ID

echo "Enabling required APIs..."
gcloud services enable pubsub.googleapis.com
gcloud services enable dataflow.googleapis.com
gcloud services enable bigquery.googleapis.com

echo "Creating Pub/Sub topic and subscription..."
gcloud pubsub topics create $TOPIC_ID || echo "Topic already exists."
gcloud pubsub subscriptions create $SUBSCRIPTION_ID --topic=$TOPIC_ID || echo "Subscription already exists."

echo "Creating BigQuery dataset and table..."
bq --location=$REGION mk --dataset $PROJECT_ID:$BQ_DATASET || echo "Dataset already exists."

bq query --use_legacy_sql=false "
CREATE TABLE IF NOT EXISTS \`$PROJECT_ID.$BQ_DATASET.$BQ_TABLE\` (
  user_id INT64,
  action STRING,
  timestamp FLOAT64
);"

echo "Creating Cloud Storage bucket..."
gsutil mb -l $REGION gs://$GCS_BUCKET/ || echo "Bucket may already exist."

echo "✅ GCP environment setup completed."

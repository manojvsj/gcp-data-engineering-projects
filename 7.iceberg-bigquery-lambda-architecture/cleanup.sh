#!/bin/bash

# ==========================================
# 🧹 CLEANUP SCRIPT - Lambda Architecture
# ==========================================
# This script removes ALL resources created by setup.sh
# ⚠️  RUN THIS TO AVOID ONGOING CHARGES! ⚠️
# Metastore costs ~$1/hour - don't forget to clean up!
# ==========================================

# ---- CONFIGURATION (must match setup.sh) ----
PROJECT_ID="your-project-id"
UNIQUE_KEY='stream001'
REGION="europe-west2"
NETWORK="default"

# Resource names (must match setup.sh)
GCS_BUCKET_ICEBERG="iceberg-streaming-$UNIQUE_KEY"
GCS_BUCKET_DATAFLOW="dataflow-temp-$UNIQUE_KEY"
PUBSUB_TOPIC="raw-data-stream"
PUBSUB_DLQ_TOPIC="dlq-stream"
PUBSUB_SUBSCRIPTION="dataflow-subscription"
METASTORE_NAME="iceberg-streaming-metastore"
BIGQUERY_DATASET="streaming_analytics"

echo "🧹 ========================================"
echo "🧹    LAMBDA ARCHITECTURE CLEANUP"
echo "🧹 ========================================"
echo "⚠️  This will DELETE ALL resources!"
echo "📁 Project: $PROJECT_ID"
echo "🌍 Region: $REGION"
echo "🔑 Unique Key: $UNIQUE_KEY"
echo ""
echo "📋 Resources to be deleted:"
echo "   • Dataflow jobs (if running)"
echo "   • Pub/Sub topics and subscriptions"
echo "   • GCS buckets: $GCS_BUCKET_ICEBERG, $GCS_BUCKET_DATAFLOW"
echo "   • BigQuery dataset: $BIGQUERY_DATASET"
echo "   • Dataproc Metastore: $METASTORE_NAME"
echo "   • BigLake connections"
echo ""

# Confirmation prompt
read -p "⚠️  Are you sure you want to DELETE all resources? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cleanup cancelled by user"
    exit 1
fi

echo ""
echo "🚀 Starting cleanup process..."
echo ""

# ---- STEP 1: STOP RUNNING DATAFLOW JOBS ----
echo "🛑 Step 1: Stopping Dataflow jobs..."
echo "Listing running Dataflow jobs..."

# Get running jobs
RUNNING_JOBS=$(gcloud dataflow jobs list \
    --region=$REGION \
    --project=$PROJECT_ID \
    --status=active \
    --format="value(id)")

if [ -z "$RUNNING_JOBS" ]; then
    echo "ℹ️  No running Dataflow jobs found"
else
    echo "Found running jobs, attempting to cancel..."
    for job_id in $RUNNING_JOBS; do
        echo "Cancelling job: $job_id"
        gcloud dataflow jobs cancel $job_id \
            --region=$REGION \
            --project=$PROJECT_ID || echo "⚠️  Failed to cancel job $job_id"
    done
fi

echo "✅ Step 1 completed: Dataflow jobs"
echo ""

# ---- STEP 2: DELETE PUB/SUB RESOURCES ----
echo "📮 Step 2: Deleting Pub/Sub resources..."

# Delete subscription first (dependent on topic)
echo "Deleting subscription: $PUBSUB_SUBSCRIPTION"
gcloud pubsub subscriptions delete $PUBSUB_SUBSCRIPTION \
    --project=$PROJECT_ID \
    --quiet || echo "⚠️  Subscription may not exist"

# Delete topics
echo "Deleting topic: $PUBSUB_TOPIC"
gcloud pubsub topics delete $PUBSUB_TOPIC \
    --project=$PROJECT_ID \
    --quiet || echo "⚠️  Topic may not exist"

echo "Deleting DLQ topic: $PUBSUB_DLQ_TOPIC"
gcloud pubsub topics delete $PUBSUB_DLQ_TOPIC \
    --project=$PROJECT_ID \
    --quiet || echo "⚠️  DLQ topic may not exist"

echo "✅ Step 2 completed: Pub/Sub resources"
echo ""

# ---- STEP 3: DELETE GCS BUCKETS ----
echo "🪣 Step 3: Deleting GCS buckets..."

# Delete Iceberg bucket (with all contents)
echo "Deleting bucket: gs://$GCS_BUCKET_ICEBERG"
gsutil -m rm -r gs://$GCS_BUCKET_ICEBERG || echo "⚠️  Bucket may not exist"

# Delete Dataflow temp bucket (with all contents)
echo "Deleting bucket: gs://$GCS_BUCKET_DATAFLOW"
gsutil -m rm -r gs://$GCS_BUCKET_DATAFLOW || echo "⚠️  Bucket may not exist"

echo "✅ Step 3 completed: GCS buckets"
echo ""

# ---- STEP 4: DELETE BIGQUERY RESOURCES ----
echo "🗃️  Step 4: Deleting BigQuery resources..."

# Delete BigQuery dataset (with all tables)
echo "Deleting BigQuery dataset: $BIGQUERY_DATASET"
bq rm -r -f $PROJECT_ID:$BIGQUERY_DATASET || echo "⚠️  Dataset may not exist"

# Delete BigLake connection
echo "Deleting BigLake connection: biglake_streaming_connection"
bq rm --connection \
    --location=$REGION \
    --project_id=$PROJECT_ID \
    biglake_streaming_connection || echo "⚠️  Connection may not exist"

echo "✅ Step 4 completed: BigQuery resources"
echo ""

# ---- STEP 5: DELETE DATAPROC METASTORE (EXPENSIVE!) ----
echo "🗄️  Step 5: Deleting Dataproc Metastore..."
echo "⚠️  This is the most expensive resource (~$1/hour)"

# Check if metastore exists first
METASTORE_EXISTS=$(gcloud metastore services describe $METASTORE_NAME \
    --location=$REGION \
    --project=$PROJECT_ID \
    --format="value(name)" 2>/dev/null || echo "")

if [ -z "$METASTORE_EXISTS" ]; then
    echo "ℹ️  Metastore not found or already deleted"
else
    echo "Deleting Dataproc Metastore: $METASTORE_NAME"
    echo "⏳ This may take 5-10 minutes..."

    gcloud metastore services delete $METASTORE_NAME \
        --location=$REGION \
        --project=$PROJECT_ID \
        --quiet

    if [ $? -eq 0 ]; then
        echo "✅ Metastore deletion initiated"
    else
        echo "❌ Failed to delete metastore - check manually!"
        echo "💰 IMPORTANT: Delete manually to avoid charges!"
    fi
fi

echo "✅ Step 5 completed: Dataproc Metastore"
echo ""

# ---- STEP 6: CLEANUP VERIFICATION ----
echo "🔍 Step 6: Cleanup verification..."

echo ""
echo "📋 Checking remaining resources..."

# Check for any remaining buckets
echo "🪣 Checking GCS buckets..."
REMAINING_BUCKETS=$(gsutil ls -p $PROJECT_ID | grep -E "(iceberg-streaming|dataflow-temp)" || echo "")
if [ -z "$REMAINING_BUCKETS" ]; then
    echo "✅ No project buckets found"
else
    echo "⚠️  Found remaining buckets:"
    echo "$REMAINING_BUCKETS"
fi

# Check for remaining Pub/Sub topics
echo ""
echo "📮 Checking Pub/Sub topics..."
REMAINING_TOPICS=$(gcloud pubsub topics list --project=$PROJECT_ID --format="value(name)" | grep -E "(raw-data-stream|dlq-stream)" || echo "")
if [ -z "$REMAINING_TOPICS" ]; then
    echo "✅ No project topics found"
else
    echo "⚠️  Found remaining topics:"
    echo "$REMAINING_TOPICS"
fi

# Check for remaining BigQuery datasets
echo ""
echo "🗃️  Checking BigQuery datasets..."
REMAINING_DATASETS=$(bq ls --project_id=$PROJECT_ID --format=json | grep -o "\"datasetId\":\s*\"[^\"]*\"" | grep streaming || echo "")
if [ -z "$REMAINING_DATASETS" ]; then
    echo "✅ No streaming datasets found"
else
    echo "⚠️  Found remaining datasets:"
    echo "$REMAINING_DATASETS"
fi

# Check metastore status
echo ""
echo "🗄️  Checking Metastore status..."
METASTORE_STATUS=$(gcloud metastore services describe $METASTORE_NAME \
    --location=$REGION \
    --project=$PROJECT_ID \
    --format="value(state)" 2>/dev/null || echo "NOT_FOUND")

if [ "$METASTORE_STATUS" = "NOT_FOUND" ]; then
    echo "✅ Metastore successfully deleted"
elif [ "$METASTORE_STATUS" = "DELETING" ]; then
    echo "⏳ Metastore deletion in progress..."
else
    echo "⚠️  Metastore still exists with status: $METASTORE_STATUS"
    echo "💰 CHECK MANUALLY: https://console.cloud.google.com/dataproc/metastore"
fi

echo ""
echo "🎉 ========================================"
echo "🎉    CLEANUP PROCESS COMPLETED!"
echo "🎉 ========================================"
echo ""
echo "✅ Summary of cleanup actions:"
echo "   • Dataflow jobs: Cancelled"
echo "   • Pub/Sub topics: Deleted"
echo "   • GCS buckets: Deleted"
echo "   • BigQuery datasets: Deleted"
echo "   • Metastore: Deleted/Deleting"
echo ""
echo "📋 Manual verification recommended:"
echo "   🌐 GCP Console: https://console.cloud.google.com"
echo "   📊 Billing: https://console.cloud.google.com/billing"
echo "   🗄️  Metastore: https://console.cloud.google.com/dataproc/metastore"
echo ""
echo "💰 Cost Impact:"
echo "   • Most resources: $0 ongoing cost"
echo "   • Metastore: Was ~$1/hour (now deleted)"
echo "   • Storage: Small residual costs may apply"
echo ""

# Final warning about manual checks
if [ "$METASTORE_STATUS" != "NOT_FOUND" ]; then
    echo "⚠️  IMPORTANT WARNING:"
    echo "   Metastore may still be running!"
    echo "   Check manually and delete if needed:"
    echo "   gcloud metastore services delete $METASTORE_NAME --location=$REGION"
    echo ""
fi

echo "🏁 Cleanup script finished!"
echo "💡 Tip: Regularly check your GCP billing dashboard"
echo "📧 Consider setting up billing alerts for future projects"
echo ""

# Cleanup Script for Project 5/50: Data Quality Checks
# ---------------------------------------

# Set your variables
PROJECT_ID="your project name"
DATASET="data_quality"
TABLE="data_quality_results"
FUNCTION_NAME="dq_checker"
REGION=europe-west2
SCHEDULER_NAME="trigger-dq-checks"

echo "🔄 Starting cleanup..."

# Delete Cloud Scheduler Job
echo "🧹 Deleting Cloud Scheduler job: $SCHEDULER_JOB"
gcloud scheduler jobs delete $SCHEDULER_NAME \
  --location=$REGION --project=$PROJECT_ID --quiet

# Delete Cloud Function
echo "🧹 Deleting Cloud Function: $CLOUD_FUNCTION"
gcloud functions delete $FUNCTION_NAME \
  --region=$REGION --project=$PROJECT_ID --quiet

# Delete BigQuery Table
echo "🧹 Deleting BigQuery Table: $PROJECT_ID.$DATASET.$TABLE"
bq rm -f -t "$PROJECT_ID:$DATASET.$TABLE"

echo "✅ Cleanup complete."
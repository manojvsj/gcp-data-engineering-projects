#!/bin/bash

# ============================================
# Cleanup Script
# ============================================
# This script removes all resources created by setup.sh
# WARNING: This will delete BigQuery data, Cloud Run services, and service accounts
# ============================================

# Check if required variables are set
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: PROJECT_ID environment variable not set."
    echo ""
    echo "Please set PROJECT_ID before running cleanup:"
    echo "  export PROJECT_ID='your-project-id'"
    echo "  ./cleanup.sh"
    exit 1
fi

# Set defaults if not provided
REGION="${REGION:-us-central1}"
DATASET_ID="${DATASET_ID:-sales_data}"
MCP_SERVICE_NAME="${MCP_SERVICE_NAME:-mcp-bigquery-server}"
STREAMLIT_SERVICE_NAME="${STREAMLIT_SERVICE_NAME:-streamlit-app}"
MCP_SA_NAME="${MCP_SA_NAME:-mcp-bq-sa}"
STREAMLIT_SA_NAME="${STREAMLIT_SA_NAME:-streamlit-sa}"

echo "🧹 Cleanup Script"
echo "=================================="
echo "⚠️  WARNING: This will delete the following resources:"
echo ""
echo "Cloud Run Services:"
echo "  - $MCP_SERVICE_NAME"
echo "  - $STREAMLIT_SERVICE_NAME"
echo ""
echo "Service Accounts:"
echo "  - $MCP_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
echo "  - $STREAMLIT_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
echo ""
echo "BigQuery Dataset (optional):"
echo "  - $PROJECT_ID:$DATASET_ID (with all tables)"
echo ""
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "=================================="
echo ""

# Prompt for confirmation
read -p "Are you sure you want to proceed? (type 'yes' to confirm): " confirmation

if [ "$confirmation" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "Starting cleanup..."

# Set project
gcloud config set project $PROJECT_ID

# ============================================
# Delete Cloud Run Services
# ============================================
echo ""
echo "🗑️  Deleting Cloud Run services..."

gcloud run services delete $MCP_SERVICE_NAME \
  --region=$REGION \
  --quiet 2>/dev/null && echo "  ✅ Deleted $MCP_SERVICE_NAME" || echo "  ⚠️  $MCP_SERVICE_NAME not found"

gcloud run services delete $STREAMLIT_SERVICE_NAME \
  --region=$REGION \
  --quiet 2>/dev/null && echo "  ✅ Deleted $STREAMLIT_SERVICE_NAME" || echo "  ⚠️  $STREAMLIT_SERVICE_NAME not found"

# ============================================
# Delete Service Accounts
# ============================================
echo ""
echo "🗑️  Deleting service accounts..."

# Remove IAM policy bindings first
MCP_SA_EMAIL="$MCP_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
STREAMLIT_SA_EMAIL="$STREAMLIT_SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

echo "  Removing IAM policy bindings..."

gcloud projects remove-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$MCP_SA_EMAIL" \
  --role="roles/bigquery.dataViewer" \
  --quiet 2>/dev/null || true

gcloud projects remove-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$MCP_SA_EMAIL" \
  --role="roles/bigquery.jobUser" \
  --quiet 2>/dev/null || true

gcloud projects remove-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$STREAMLIT_SA_EMAIL" \
  --role="roles/aiplatform.user" \
  --quiet 2>/dev/null || true

# Delete service accounts
gcloud iam service-accounts delete $MCP_SA_EMAIL \
  --quiet 2>/dev/null && echo "  ✅ Deleted $MCP_SA_EMAIL" || echo "  ⚠️  $MCP_SA_EMAIL not found"

gcloud iam service-accounts delete $STREAMLIT_SA_EMAIL \
  --quiet 2>/dev/null && echo "  ✅ Deleted $STREAMLIT_SA_EMAIL" || echo "  ⚠️  $STREAMLIT_SA_EMAIL not found"

# ============================================
# Delete BigQuery Dataset (Optional)
# ============================================
echo ""
read -p "Do you want to delete the BigQuery dataset '$DATASET_ID'? (yes/no): " delete_bq

if [ "$delete_bq" = "yes" ]; then
    echo "🗑️  Deleting BigQuery dataset..."
    bq rm -r -f -d $PROJECT_ID:$DATASET_ID 2>/dev/null && \
      echo "  ✅ Deleted dataset $PROJECT_ID:$DATASET_ID" || \
      echo "  ⚠️  Dataset $PROJECT_ID:$DATASET_ID not found"
else
    echo "  ⏭️  Skipping BigQuery dataset deletion"
fi

# ============================================
# Summary
# ============================================
echo ""
echo "✅ Cleanup Complete!"
echo "=================================="
echo "The following resources have been removed:"
echo "  - Cloud Run services"
echo "  - Service accounts and IAM bindings"
if [ "$delete_bq" = "yes" ]; then
    echo "  - BigQuery dataset and tables"
fi
echo ""
echo "Note: Enabled APIs have NOT been disabled."
echo "To disable APIs manually, run:"
echo ""
echo "gcloud services disable bigquery.googleapis.com --force"
echo "gcloud services disable run.googleapis.com --force"
echo "gcloud services disable aiplatform.googleapis.com --force"
echo "=================================="

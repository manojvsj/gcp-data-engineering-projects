#!/bin/bash

# ============================================
# Infrastructure Setup Script
# ============================================

# Load environment variables
if [ -f "../.env" ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
fi

# Set defaults
: ${PROJECT_ID:?'PROJECT_ID not set'}
: ${REGION:='us-central1'}
: ${DATASET_ID:='sales_data'}
: ${TABLE_ID:='orders'}

echo "🏗️  Setting up GCP infrastructure..."
echo "Project: $PROJECT_ID"
echo ""

# Set the active GCP project
gcloud config set project $PROJECT_ID

# ============================================
# Enable Required APIs
# ============================================
echo "📦 Enabling GCP APIs..."
gcloud services enable \
  bigquery.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  generativelanguage.googleapis.com

# ============================================
# Create Service Accounts
# ============================================
echo "👤 Creating Service Accounts..."

gcloud iam service-accounts create mcp-bq-sa \
  --display-name="MCP BigQuery SA" \
  2>/dev/null || echo "Service account mcp-bq-sa already exists"

gcloud iam service-accounts create streamlit-sa \
  --display-name="Streamlit App SA" \
  2>/dev/null || echo "Service account streamlit-sa already exists"

# Get Service Account Emails
export MCP_SA_EMAIL=$(gcloud iam service-accounts list --filter="name:mcp-bq-sa" --format="value(email)")
export STREAMLIT_SA_EMAIL=$(gcloud iam service-accounts list --filter="name:streamlit-sa" --format="value(email)")

# ============================================
# Grant IAM Permissions
# ============================================
echo "🔐 Granting IAM permissions..."

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$MCP_SA_EMAIL" \
  --role="roles/bigquery.dataViewer" \
  --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$MCP_SA_EMAIL" \
  --role="roles/bigquery.jobUser" \
  --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$STREAMLIT_SA_EMAIL" \
  --role="roles/aiplatform.user" \
  --condition=None

# ============================================
# Setup BigQuery
# ============================================
echo "📊 Setting up BigQuery..."
chmod +x bigquery-setup.sh
./bigquery-setup.sh

echo ""
echo "✅ Infrastructure setup complete!"
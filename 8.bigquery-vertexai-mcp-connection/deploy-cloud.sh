#!/bin/bash

# Deploy to Google Cloud Run

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Validate required variables
: ${PROJECT_ID:?'PROJECT_ID not set'}
: ${REGION:='us-central1'}

echo "🚀 Deploying to Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Set the active GCP project
gcloud config set project $PROJECT_ID

# Run infrastructure setup
echo "📦 Setting up infrastructure..."
cd setup-infra
./setup.sh
cd ..

# Get Service Account Emails
export MCP_SA_EMAIL=$(gcloud iam service-accounts list --filter="name:mcp-bq-sa" --format="value(email)")
export STREAMLIT_SA_EMAIL=$(gcloud iam service-accounts list --filter="name:streamlit-sa" --format="value(email)")

# ============================================
# Deploy MCP BigQuery Server to Cloud Run
# ============================================
echo "🚢 Deploying MCP BigQuery Server..."

cd mcp-bigquery-server

gcloud run deploy mcp-bigquery-server \
  --source . \
  --region $REGION \
  --platform managed \
  --no-allow-unauthenticated \
  --service-account=$MCP_SA_EMAIL \
  --set-env-vars="PROJECT_ID=$PROJECT_ID,DATASET_ID=${DATASET_ID:-sales_data},TABLE_ID=${TABLE_ID:-orders}" \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300 \
  --max-instances=10 \
  --min-instances=0

# Get the MCP Server URL
export MCP_SERVER_URL=$(gcloud run services describe mcp-bigquery-server \
  --region=$REGION \
  --format="value(status.url)")

echo "MCP Server URL: $MCP_SERVER_URL"

cd ..

# ============================================
# Deploy Streamlit App to Cloud Run
# ============================================
echo "🚢 Deploying Streamlit App..."

cd streamlit-app

gcloud run deploy streamlit-app \
  --source . \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --service-account=$STREAMLIT_SA_EMAIL \
  --set-env-vars="PROJECT_ID=$PROJECT_ID,REGION=$REGION,LOCATION=${LOCATION:-us-central1},MCP_SERVER_URL=$MCP_SERVER_URL,DATASET_ID=${DATASET_ID:-sales_data},TABLE_ID=${TABLE_ID:-orders},VERTEX_AI_MODEL=${VERTEX_AI_MODEL:-gemini-1.5-flash}" \
  --memory=1Gi \
  --cpu=1 \
  --timeout=300 \
  --max-instances=10 \
  --min-instances=0 \
  --port=8501

# Get the Streamlit App URL
export STREAMLIT_APP_URL=$(gcloud run services describe streamlit-app \
  --region=$REGION \
  --format="value(status.url)")

cd ..

# ============================================
# Grant Cloud Run Invoker Role
# ============================================
echo "🔑 Granting invoker permissions..."

gcloud run services add-iam-policy-binding mcp-bigquery-server \
  --region=$REGION \
  --member="serviceAccount:$STREAMLIT_SA_EMAIL" \
  --role="roles/run.invoker"

# ============================================
# Summary
# ============================================
echo ""
echo "✅ Deployment Complete!"
echo "=================================="
echo "MCP Server: $MCP_SERVER_URL"
echo "Streamlit App: $STREAMLIT_APP_URL"
echo ""
echo "⚠️  Grant yourself access:"
echo "gcloud run services add-iam-policy-binding streamlit-app \\"
echo "  --region=$REGION \\"
echo "  --member='user:YOUR-EMAIL@example.com' \\"
echo "  --role='roles/run.invoker'"
echo "=================================="

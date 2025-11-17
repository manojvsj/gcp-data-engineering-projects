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
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Build environment variables string
ENV_VARS="GOOGLE_CLOUD_PROJECT=${PROJECT_ID}"

# Add location if set
if [ -n "$GOOGLE_CLOUD_LOCATION" ]; then
    ENV_VARS="${ENV_VARS},GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION}"
fi

# Check if using Vertex AI or API Key
if [ "${GOOGLE_GENAI_USE_VERTEXAI}" = "TRUE" ]; then
    echo "Using Vertex AI..."
    ENV_VARS="${ENV_VARS},GOOGLE_GENAI_USE_VERTEXAI=TRUE"
else
    if [ -z "$GOOGLE_API_KEY" ]; then
        echo "Error: GOOGLE_API_KEY not set"
        echo "Run: export GOOGLE_API_KEY='your-api-key'"
        echo "Or set GOOGLE_GENAI_USE_VERTEXAI=TRUE in .env to use Vertex AI"
        exit 1
    fi
    ENV_VARS="${ENV_VARS},GOOGLE_API_KEY=${GOOGLE_API_KEY}"
fi

echo "Building image..."
gcloud config set project $PROJECT_ID
gcloud builds submit --tag $IMAGE_NAME .

echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --service-account $SERVICE_ACCOUNT_EMAIL \
    --memory 512Mi \
    --timeout 300 \
    --set-env-vars "${ENV_VARS}"

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
echo "Deployed at: $SERVICE_URL"

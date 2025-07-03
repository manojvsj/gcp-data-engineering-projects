#!/bin/bash

# Set variables
PROJECT_ID="your-project-id"
REGION="your-region"
CLUSTER_NAME="your-cluster-name"
MAIN_PY="gs://your-bucket/path-to-your-script.py"
INPUT_PATH="gs://your-bucket/input-path"
OUTPUT_PATH="gs://your-bucket/output-path"

# Submit the PySpark job
echo "📦 Submitting PySpark job to Dataproc..."
JOB_ID=$(gcloud dataproc jobs submit pyspark "$MAIN_PY" \
    --cluster="$CLUSTER_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --properties spark.driver.memory=4g \
    -- \
    --input_path="$INPUT_PATH" \
    --output_path="$OUTPUT_PATH" \
    --format="value(reference.jobId)")

echo "✅ Dataproc job submitted with Job ID: $JOB_ID"

# Wait for the job to complete
echo "🔍 Waiting for job to complete..."
while true; do
    JOB_STATUS=$(gcloud dataproc jobs describe "$JOB_ID" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --format="value(status.state)")

    echo "   Current job status: $JOB_STATUS"

    if [[ "$JOB_STATUS" == "DONE" ]]; then
        echo "✅ Job finished successfully!"
        break
    elif [[ "$JOB_STATUS" == "ERROR" ]]; then
        echo "❌ Job failed!"
        exit 1
    elif [[ "$JOB_STATUS" == "CANCELLED" ]]; then
        echo "⚠️ Job was cancelled!"
        exit 1
    fi

    sleep 10
done

# Delete the cluster
echo "🧹 Deleting cluster: $CLUSTER_NAME..."
gcloud dataproc clusters delete "$CLUSTER_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --quiet

echo "✅ Cluster deleted successfully!"
#!/bin/bash
# Example: How to run the simple streaming pipeline
#
# Apache Beam automatically parses these command line arguments
# when you call PipelineOptions() with no parameters

# Replace these values with your actual GCP resources:
PROJECT_ID="<your-project-id>"
REGION="europe-west2"
TEMP_BUCKET="dataflow-temp-stream001"
INPUT_TOPIC="projects/<your-project-id>/topics/raw-data-stream"
BQ_DATASET="streaming_analytics"

echo "🚀 Running Simple Streaming Pipeline"
echo "=================================="
echo "This uses Apache Beam's automatic command line parsing"
echo ""

python3 streaming_pipeline.py \
  --project=$PROJECT_ID \
  --region=$REGION \
  --runner=DataflowRunner \
  --temp_location=gs://$TEMP_BUCKET/tmp \
  --staging_location=gs://$TEMP_BUCKET/staging \
  --streaming \
  --job_name=simple-streaming-$(date +%s) \
  --maxNumWorkers=2

echo ""
echo "✨ How this works:"
echo "1. PipelineOptions() automatically parses command line arguments"
echo "2. No need for argparse or manual argument handling"
echo "3. Apache Beam handles all the --project, --region, --runner flags"
echo "4. Your pipeline just focuses on the data processing logic"

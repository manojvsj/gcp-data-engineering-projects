# Simple Streaming Pipeline - Command Line Arguments

## How Apache Beam Automatic Argument Parsing Works

When you create `PipelineOptions()` without any arguments, Apache Beam automatically parses `sys.argv` (command line arguments). This is much cleaner than using argparse!

## The Magic Behind the Scenes

```python
# This line automatically parses all --flag=value arguments from command line
pipeline_options = PipelineOptions()

# Apache Beam recognizes these standard flags:
# --project=YOUR_PROJECT_ID
# --region=YOUR_REGION
# --runner=DataflowRunner
# --temp_location=gs://bucket/tmp
# --streaming
# --job_name=my-job
# etc.
```

## How to Run the Pipeline

```bash
python3 streaming_pipeline.py \
  --project=<project-id> \
  --region=europe-west2 \
  --runner=DataflowRunner \
  --temp_location=gs://your-bucket/tmp \
  --staging_location=gs://your-bucket/staging \
  --streaming \
  --job_name=simple-streaming-test
```

## Local vs Dataflow Runner

**Local testing (DirectRunner):**
```bash
python3 streaming_pipeline.py --runner=DirectRunner
```

**Cloud Dataflow:**
```bash
python3 streaming_pipeline.py \
  --project=YOUR_PROJECT \
  --region=YOUR_REGION \
  --runner=DataflowRunner \
  --temp_location=gs://YOUR_BUCKET/tmp
```

## What Makes This Simple

1. **No argparse needed** - Apache Beam handles argument parsing
2. **No hardcoded values** - Everything comes from command line
3. **Standard Dataflow patterns** - Uses the same format as Google examples
4. **Flexible** - Easy to switch between local and cloud execution

## Available Command Line Options

| Flag | Description | Example |
|------|-------------|---------|
| `--project` | GCP Project ID | `--project=my-project` |
| `--region` | GCP Region | `--region=us-central1` |
| `--runner` | Pipeline runner | `--runner=DataflowRunner` |
| `--temp_location` | Temp GCS path | `--temp_location=gs://bucket/tmp` |
| `--staging_location` | Staging GCS path | `--staging_location=gs://bucket/staging` |
| `--streaming` | Enable streaming mode | `--streaming` |
| `--job_name` | Dataflow job name | `--job_name=my-job` |

## Quick Start

1. **Update the dataflow script:**
   ```bash
   nano run_dataflow.sh
   # Update PROJECT_ID, REGION, TEMP_BUCKET with your values
   ```

2. **Make it executable:**
   ```bash
   chmod +x run_dataflow.sh
   ```

3. **Run the pipeline:**
   ```bash
   ./run_dataflow.sh
   ```

This approach is much cleaner and follows Google Cloud's best practices!

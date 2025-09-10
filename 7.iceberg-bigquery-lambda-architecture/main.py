#!/usr/bin/env python3
"""
Simple Lambda Architecture Pipeline Orchestrator
Manages the streaming pipeline deployment and monitoring
"""

import subprocess
import yaml
import logging
import time
from google.cloud import dataflow_v1beta3
from google.cloud import pubsub_v1

def load_config():
    """Load configuration from config.yaml"""
    with open('config/config.yaml', 'r') as file:
        return yaml.safe_load(file)

def check_pubsub_topic(project_id, topic_name):
    """Check if Pub/Sub topic exists and has messages"""
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_name.split('/')[-1])

        # Try to get topic info
        topic = publisher.get_topic(request={"topic": topic_path})
        print(f"✅ Pub/Sub topic exists: {topic.name}")
        return True

    except Exception as e:
        print(f"❌ Pub/Sub topic issue: {e}")
        return False

def deploy_streaming_pipeline(config):
    """Deploy the Dataflow streaming pipeline"""
    try:
        print("🚀 Deploying Dataflow streaming pipeline...")

        # Build the command
        cmd = [
            'python', 'dataflow_jobs/streaming_pipeline.py',
            f'--project={config["project"]["id"]}',
            f'--region={config["project"]["region"]}',
            f'--temp_location={config["dataflow"]["temp_location"]}',
            f'--staging_location={config["dataflow"]["staging_location"]}',
            f'--job_name={config["dataflow"]["job_name"]}',
            f'--max_num_workers={config["dataflow"]["max_num_workers"]}',
            '--streaming',
            '--runner=DataflowRunner'
        ]

        print(f"Command: {' '.join(cmd)}")

        # Execute the pipeline
        result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')

        if result.returncode == 0:
            print("✅ Pipeline deployed successfully!")
            print("Job output:", result.stdout)
            return True
        else:
            print("❌ Pipeline deployment failed!")
            print("Error:", result.stderr)
            return False

    except Exception as e:
        print(f"❌ Error deploying pipeline: {e}")
        return False

def run_local_pipeline(config):
    """Run pipeline locally with DirectRunner for testing"""
    try:
        print("🧪 Running pipeline locally for testing...")

        cmd = [
            'python', 'dataflow_jobs/streaming_pipeline.py',
            f'--project={config["project"]["id"]}',
            '--runner=DirectRunner',
            '--streaming'
        ]

        print(f"Command: {' '.join(cmd)}")
        print("Note: Local streaming runs indefinitely. Press Ctrl+C to stop.")

        # Run locally (this will run until interrupted)
        subprocess.run(cmd, cwd='.')

    except KeyboardInterrupt:
        print("\n⏹️  Local pipeline stopped by user")
    except Exception as e:
        print(f"❌ Error running local pipeline: {e}")

def check_pipeline_status(project_id, region, job_name):
    """Check the status of the deployed Dataflow job"""
    try:
        client = dataflow_v1beta3.JobsV1Beta3Client()

        # List jobs to find our job
        request = dataflow_v1beta3.ListJobsRequest(
            project_id=project_id,
            location=region
        )

        jobs = client.list_jobs(request=request)

        for job in jobs:
            if job.name.startswith(job_name):
                print(f"📊 Job: {job.name}")
                print(f"   Status: {job.current_state.name}")
                print(f"   Created: {job.create_time}")
                return job.current_state.name

        print("❌ No matching jobs found")
        return None

    except Exception as e:
        print(f"❌ Error checking pipeline status: {e}")
        return None

def main():
    """Main orchestrator function"""
    print("=== Lambda Architecture Pipeline Orchestrator ===")

    # Load configuration
    try:
        config = load_config()
        print(f"📋 Configuration loaded for project: {config['project']['id']}")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return

    # Menu
    while True:
        print("\n" + "="*50)
        print("Choose an option:")
        print("1. Deploy streaming pipeline to Dataflow")
        print("2. Run pipeline locally (testing)")
        print("3. Check pipeline status")
        print("4. Test Pub/Sub topic")
        print("5. Exit")

        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            # Deploy to Dataflow
            success = deploy_streaming_pipeline(config)
            if success:
                print("\n✅ Pipeline deployed! Monitor at:")
                print(f"https://console.cloud.google.com/dataflow/jobs?project={config['project']['id']}")

        elif choice == "2":
            # Run locally
            run_local_pipeline(config)

        elif choice == "3":
            # Check status
            check_pipeline_status(
                config['project']['id'],
                config['project']['region'],
                config['dataflow']['job_name']
            )

        elif choice == "4":
            # Test Pub/Sub
            topic_name = config['pubsub']['input_topic']
            check_pubsub_topic(config['project']['id'], topic_name)

        elif choice == "5":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
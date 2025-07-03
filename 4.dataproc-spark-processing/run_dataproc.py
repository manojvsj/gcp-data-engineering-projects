import time
import uuid
from google.cloud import dataproc_v1
from google.cloud import storage
from google.api_core.exceptions import NotFound
from google.protobuf.duration_pb2 import Duration


PROJECT_ID = "your project id"
UNIQUE_KEY = "adsf"
REGION = "europe-west2"
CLUSTER_NAME = f"gcp-learning-4-cluster"
BUCKET_NAME = f"dataproc-learning-{UNIQUE_KEY}"
PYSCRIPT_LOCAL = "pyspark_job.py"
PYSCRIPT_GCS = f"dataproc/jobs/{PYSCRIPT_LOCAL}"
INPUT_PATH = f"gs://{BUCKET_NAME}/input/orders_data.csv"
OUTPUT_PATH = f"gs://{BUCKET_NAME}/output/sales_partitioned"

def upload_script_to_gcs():
    print(f" Uploading {PYSCRIPT_LOCAL} to GCS...")
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(PYSCRIPT_GCS)
    blob.upload_from_filename(PYSCRIPT_LOCAL)

def create_cluster():
    print(f"🚀 Creating cluster: {CLUSTER_NAME}")

    # Initialise the client with the correct regional endpoint
    cluster_client = dataproc_v1.ClusterControllerClient(
        client_options={"api_endpoint": f"{REGION}-dataproc.googleapis.com:443"}
    )

    # Define the idle timeout duration (15 minutes)
    idle_timeout = Duration(seconds=15 * 60)

    # Correctly structure the CreateClusterRequest
    cluster_config = dataproc_v1.Cluster(
        cluster_name=CLUSTER_NAME,
        config=dataproc_v1.ClusterConfig(
            master_config=dataproc_v1.InstanceGroupConfig(
                num_instances=1,
                machine_type_uri="n1-standard-4",
            ),
            software_config=dataproc_v1.SoftwareConfig(
                image_version="2.1-debian11"
            ),
            lifecycle_config=dataproc_v1.LifecycleConfig(
                idle_delete_ttl=idle_timeout  # Automatically delete after 15 mins of idleness
            )
        )
    )

    # Call the create_cluster method with appropriate parameters
    operation = cluster_client.create_cluster(
        request={
            "project_id": PROJECT_ID,
            "region": REGION,
            "cluster": cluster_config,
        }
    )

    # Wait for the operation to complete
    operation.result()
    print("✅ Cluster created.")

def submit_pyspark_job():
    print("📦 Submitting PySpark job...")

    # Initialise the JobControllerClient
    job_client = dataproc_v1.JobControllerClient(
        client_options={"api_endpoint": f"{REGION}-dataproc.googleapis.com:443"}
    )

    # Define the job details
    job_details = dataproc_v1.Job(
        placement={"cluster_name": CLUSTER_NAME},
        pyspark_job={
            "main_python_file_uri": f"gs://{BUCKET_NAME}/{PYSCRIPT_GCS}",
            "args": [
                "--input_path", INPUT_PATH,
                "--output_path", OUTPUT_PATH,
            ],
            "properties": {
            "spark.driver.memory": "4g",  # Set driver memory to 4 GB
            "spark.executor.memory": "4g"  # Set executor memory to 4 GB
            }
        }
    )

    # Submit the job
    result = job_client.submit_job(
        project_id=PROJECT_ID,
        region=REGION,
        job=job_details
    )

    # Retrieve the job ID
    job_id = result.reference.job_id
    print(f"⏳ Job submitted: {job_id}")
    return job_id

def wait_for_job_completion(job_id):
    print("🔍 Waiting for job to complete...")

    # Create the JobControllerClient
    job_client = dataproc_v1.JobControllerClient(
        client_options={"api_endpoint": f"{REGION}-dataproc.googleapis.com:443"}
    )

    while True:
        # Fetch the current job status
        job = job_client.get_job(project_id=PROJECT_ID, region=REGION, job_id=job_id)
        state = job.status.state

        # Convert the state to a human-readable string
        state_name = dataproc_v1.JobStatus.State(state).name
        print(f"   Current state: {state_name}")

        if state in {dataproc_v1.JobStatus.State.DONE, dataproc_v1.JobStatus.State.ERROR, dataproc_v1.JobStatus.State.CANCELLED}:
            break

        time.sleep(10)

    # Handle terminal states
    if state == dataproc_v1.JobStatus.State.DONE:
        print("✅ Job finished successfully.")
    elif state == dataproc_v1.JobStatus.State.ERROR:
        print("❌ Job failed.")
        raise RuntimeError(f"Job {job_id} failed with error: {job.status.details}")
    elif state == dataproc_v1.JobStatus.State.CANCELLED:
        print("⚠️ Job was cancelled.")
        raise RuntimeError(f"Job {job_id} was cancelled.")

def delete_cluster():
    print(f"🧹 Deleting cluster: {CLUSTER_NAME}")

    # Create the ClusterControllerClient
    cluster_client = dataproc_v1.ClusterControllerClient(
        client_options={"api_endpoint": f"{REGION}-dataproc.googleapis.com:443"}
    )

    try:
        # Request to delete the cluster
        operation = cluster_client.delete_cluster(
            project_id=PROJECT_ID,
            region=REGION,
            cluster_name=CLUSTER_NAME,
        )
        # Wait for the operation to complete
        operation.result()
        print("✅ Cluster deleted.")
    except NotFound:
        print("⚠️ Cluster not found. It may have already been deleted.")

def main():
    upload_script_to_gcs()
    create_cluster()
    job_id = submit_pyspark_job()
    wait_for_job_completion(job_id)
    delete_cluster()


if __name__ == "__main__":
    main()



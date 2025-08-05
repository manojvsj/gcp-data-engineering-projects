from logging import config
import time
import yaml
from venv import create
from urllib.parse import urlparse
from google.cloud import dataproc_v1
from google.cloud import storage
from google.api_core.exceptions import NotFound
from google.cloud import bigquery


# Structured configuration
## add following to the cluster config
def get_cluster_config_dict(config, storage_config):
    return {
        "cluster_name": f"{config['dataproc']['cluster_name']}",
        "config": {
            "config_bucket": config['dataproc']['staging_bucket'],
            "gce_cluster_config": {
                "zone_uri": f"{config['region']}-a",
                "metadata": {
                    "enable-component-gateway": "true"
                },
                "internal_ip_only": False,  # Optional: Set True if using private IPs
            },
            "master_config": {
                "num_instances": config['dataproc']['num_masters'],
                "machine_type_uri": config['dataproc']['master_machine_type'],
            },
            "worker_config": {
                "num_instances": config['dataproc']['num_workers'],
                "machine_type_uri": config['dataproc']['worker_machine_type'],
                "disk_config": {
                    "boot_disk_type": "hyperdisk-balanced",
                    "boot_disk_size_gb": 100
                }
            },
            "software_config": {
                "image_version": "2.2-debian12",
                "optional_components": ["JUPYTER", "ICEBERG"]
            },
            "lifecycle_config": {
                "idle_delete_ttl": config['dataproc']['idle_timeout'],  # 10 minutes in seconds
            },
            "metastore_config": {
                "dataproc_metastore_service": f"projects/{config['project_id']}/locations/{config['region']}/services/{config['metastore_name']}"
            },
            "endpoint_config": {  # ✅ This enables gateway access in the UI
                "enable_http_port_access": True
            },
            "initialization_actions": [
            {
                "executable_file": f"gs://{storage_config['warehouse_bucket']}/{storage_config['scripts_path']}init_script.sh"
            }]
        }
    }

def upload_file_to_gcs(local_path, gcs_path):
    client = storage.Client()
    parsed_url = urlparse(gcs_path)
    gcs_bucket_name = parsed_url.netloc  # Extract bucket name
    gcs_blob_path = parsed_url.path[1:]  # Extract full path after the bucket name
    bucket = client.bucket(gcs_bucket_name)

    print(f" Uploading {local_path} to GCS...")
    blob = bucket.blob(gcs_blob_path)
    try:
        blob.upload_from_filename(local_path)
        print(f"✅ Successfully uploaded {local_path} to {gcs_path}")
    except Exception as e:
        print(f"❌ Failed to upload {local_path} to {gcs_path}: {e}")
        raise

def create_cluster(cluster_config_dict, cluster_name, project_id, region):
    print(f"🚀 Creating cluster: {cluster_name}")

    # Initialise the client with the correct regional endpoint
    cluster_client = dataproc_v1.ClusterControllerClient(
        client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
    )

    # Correctly structure the CreateClusterRequest
    cluster_config = dataproc_v1.Cluster(**cluster_config_dict)  # Use the structured configuration
    operation = cluster_client.create_cluster(
        request={
            "project_id": project_id,
            "region": region,
            "cluster": cluster_config,
        }
    )

    # Wait for the operation to complete
    operation.result()
    print("✅ Cluster created.")

def submit_pyspark_job(config, input_config_path, cluster_name, project_id, region):
    print("📦 Submitting PySpark job...")

    # Initialise the JobControllerClient
    job_client = dataproc_v1.JobControllerClient(
        client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
    )

    # Define the job details
    job_details = dataproc_v1.Job(
        placement={"cluster_name": config['gcp']['dataproc']['cluster_name']},
        pyspark_job={
            "main_python_file_uri": f"gs://{config['storage']['warehouse_bucket']}/{config['storage']['scripts_path']}/pyspark_job.py",
            "args": [
                "--input_config_path", input_config_path,
            ],
            "properties": {
            "spark.driver.memory": "4g",  # Set driver memory to 4 GB
            "spark.executor.memory": "4g"  # Set executor memory to 4 GB
            }
        }
    )
    # Submit the job
    result = job_client.submit_job(
        project_id=project_id,
        region=region,
        job=job_details
    )

    # Retrieve the job ID
    job_id = result.reference.job_id
    print(f"⏳ Job submitted: {job_id}")
    return job_id

def wait_for_job_completion(job_id, project_id, region):
    print("🔍 Waiting for job to complete...")

    # Create the JobControllerClient
    job_client = dataproc_v1.JobControllerClient(
        client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
    )

    while True:
        # Fetch the current job status
        job = job_client.get_job(project_id=project_id, region=region, job_id=job_id)
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

def delete_cluster(cluster_name, project_id, region):
    print(f"🧹 Deleting cluster: {cluster_name}")

    # Create the ClusterControllerClient
    cluster_client = dataproc_v1.ClusterControllerClient(
        client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
    )

    try:
        # Request to delete the cluster
        operation = cluster_client.delete_cluster(
            project_id=project_id,
            region=region,
            cluster_name=cluster_name,
        )
        # Wait for the operation to complete
        operation.result()
        print("✅ Cluster deleted.")
    except NotFound:
        print("⚠️ Cluster not found. It may have already been deleted.")

def create_biglake_table(config):
    """
        CREATE OR REPLACE EXTERNAL TABLE `<project_id>.sales_demo.orders`
        WITH CONNECTION `europe-west2.biglake_gcs_connection`
        OPTIONS (
        format = 'PARQUET',
        uris = ['gs://<bucket_name>/gold-biglake-parquet/*.parquet']
        );
    """
    # Initialize BigQuery client
    project_id = config['gcp']['project_id']
    region = config['gcp']['region']
    bigquery_config = config['gcp']['bigquery']
    storage_config = config['storage']
    client = bigquery.Client(project=project_id)

    # Define table ID
    table_id = f"{project_id}.{bigquery_config['dataset_name']}.{bigquery_config['external_table_name']}"

    # Define external configuration
    external_config = bigquery.ExternalConfig("PARQUET")
    external_config.source_uris = [f"gs://{storage_config['warehouse_bucket']}/{storage_config['bigquery_external_table_path']}/*.parquet"]
    external_config.connection_id = f"projects/{project_id}/locations/{region}/connections/{bigquery_config['connection']}"

    # Define table
    table = bigquery.Table(table_id)
    table.external_data_configuration = external_config

    # Create or replace the table
    table = client.create_table(table, exists_ok=True)

    print(f"External table created: {table.full_table_id}")



def main():
    # 1. Load the configuration file
    config = yaml.safe_load(open('pyspark_jobs/config.yaml'))
    if not config:
        raise ValueError("Configuration could not be loaded. Please check the GCS path and file.")

    storage_config = config['storage']
    project_id = config['gcp']['project_id']
    region = config['gcp']['region']
    cluster_name = config['gcp']['dataproc']['cluster_name']
    cluster_config_dict = get_cluster_config_dict(
        config=config['gcp'],
        storage_config=storage_config)

    # upload necessary files to GCS script path
    for file in ['pyspark_job.py', 'config.yaml', 'init_script.sh']:
        print(f"uploading {file} to GCS...")
        upload_file_to_gcs(
            local_path=f"pyspark_jobs/{file}",
            gcs_path=f"gs://{storage_config['warehouse_bucket']}/{storage_config['scripts_path']}{file}"
        )
    # Create the Dataproc cluster
    print("Creating Dataproc cluster...")
    create_cluster(
        cluster_config_dict=cluster_config_dict,
        cluster_name=cluster_name,
        project_id=project_id,
        region=region)

    # submit the PySpark job
    print("Cluster created successfully. Submitting PySpark job...")
    input_config_path = f"gs://{storage_config['warehouse_bucket']}/{storage_config['scripts_path']}config.yaml"
    job_id = submit_pyspark_job(
        config=config,
        input_config_path=input_config_path,
        cluster_name=cluster_name,
        region=region,
        project_id=project_id)

    # wait for the job to complete
    print(f"Using input config path: {input_config_path}")
    print("waiting for job completion...")
    wait_for_job_completion(
        job_id=job_id,
        project_id=project_id,
        region=region)

    # Create BigLake external table
    print("Creating BigLake external table...")
    create_biglake_table(config)

    #Clean up resources dataproc
    print("📊 Job completed successfully. Cleaning up resources...")
    delete_cluster(
        cluster_name=cluster_name,
        project_id=project_id,
        region=region)

if __name__ == "__main__":
    main()
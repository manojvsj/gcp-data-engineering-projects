def create_dataproc_job(job_name, cluster_name, region, file_uri):
    from google.cloud import dataproc_v1 as dataproc

    cluster_client = dataproc.ClusterControllerClient()
    job_client = dataproc.JobControllerClient()

    job = {
        "placement": {"cluster_name": cluster_name},
        "hadoop_job": {
            "main_class": "org.apache.hadoop.examples.WordCount",
            "jar_file_uris": [file_uri],
        },
    }

    operation = job_client.submit_job(project_id='your-project-id', region=region, job=job)
    return operation


def monitor_job(job_id, cluster_name, region):
    from google.cloud import dataproc_v1 as dataproc
    import time

    job_client = dataproc.JobControllerClient()

    while True:
        job = job_client.get_job(project_id='your-project-id', region=region, job_id=job_id)
        print(f"Job {job_id} is {job.status.state}.")
        if job.status.state in (dataproc.JobStatus.State.DONE, dataproc.JobStatus.State.ERROR):
            break
        time.sleep(10)


def delete_job(job_id, cluster_name, region):
    from google.cloud import dataproc_v1 as dataproc

    job_client = dataproc.JobControllerClient()
    job_client.delete_job(project_id='your-project-id', region=region, job_id=job_id)
    print(f"Job {job_id} deleted.")
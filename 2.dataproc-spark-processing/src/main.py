import os
from gcs.gcs_operations import upload_file, download_file, list_files
from dataproc.dataproc_operations import create_dataproc_job, monitor_job, delete_job
from biglake.biglake_operations import create_biglake_table, query_biglake_table, delete_biglake_table
from bigquery.bigquery_operations import create_bq_table, query_bq_table, delete_bq_table

def main():
    # Example GCS operations
    bucket_name = "your-gcs-bucket"
    file_to_upload = "path/to/local/file.txt"
    upload_file(bucket_name, file_to_upload)
    files = list_files(bucket_name)
    print("Files in GCS bucket:", files)

    # Example DataProc operations
    job_id = create_dataproc_job("your-cluster-name", "your-job-configuration")
    monitor_job(job_id)
    delete_job(job_id)

    # Example BigLake operations
    create_biglake_table("your-biglake-table-definition")
    biglake_data = query_biglake_table("your-query")
    print("BigLake data:", biglake_data)
    delete_biglake_table("your-biglake-table-name")

    # Example BigQuery operations
    create_bq_table("your-bq-table-definition")
    bq_data = query_bq_table("your-bq-query")
    print("BigQuery data:", bq_data)
    delete_bq_table("your-bq-table-name")

if __name__ == "__main__":
    main()
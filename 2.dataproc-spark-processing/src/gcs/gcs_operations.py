def upload_file(bucket_name, source_file_name, destination_blob_name):
    from google.cloud import storage

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

def download_file(bucket_name, source_blob_name, destination_file_name):
    from google.cloud import storage

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)
    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")

def list_files(bucket_name):
    from google.cloud import storage

    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name)

    file_list = []
    for blob in blobs:
        file_list.append(blob.name)
    return file_list
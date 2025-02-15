class DataModel:
    def __init__(self, name: str, value: float):
        self.name = name
        self.value = value

class GCSFile:
    def __init__(self, file_name: str, bucket_name: str):
        self.file_name = file_name
        self.bucket_name = bucket_name

class DataProcJob:
    def __init__(self, job_id: str, status: str):
        self.job_id = job_id
        self.status = status

class BigLakeTable:
    def __init__(self, table_name: str, schema: dict):
        self.table_name = table_name
        self.schema = schema

class BigQueryTable:
    def __init__(self, table_name: str, dataset_name: str):
        self.table_name = table_name
        self.dataset_name = dataset_name
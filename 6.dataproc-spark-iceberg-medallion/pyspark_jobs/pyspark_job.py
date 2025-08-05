from pyspark.sql import SparkSession
from pyspark.sql.functions import to_date, to_timestamp, col, sum as _sum, count as _count
from pyspark.sql.functions import col, year, month, dayofmonth, current_timestamp

import argparse
import yaml
import os
from google.cloud import storage
from urllib.parse import urlparse
from google.cloud import metastore_v1

# Function to create and configure a Spark session
def get_spark_session(metastore_uri=None, warehouse_bucket=None):
    return SparkSession.builder \
        .appName("Write Iceberg Sales Table") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog") \
        .config("spark.sql.catalog.spark_catalog.type", "hive") \
        .config("spark.sql.catalog.spark_catalog.uri", f"{metastore_uri}") \
        .config("spark.sql.warehouse.dir", f"gs://{warehouse_bucket}/warehouse") \
        .config("spark.executor.memory", "4g") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.cores", "2") \
        .config("spark.driver.cores", "2") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

# Function to load configuration from a YAML file
def load_config(path="config.yaml"):
    with open(path, "r") as file:
        return yaml.safe_load(file)

# Function to create a database if it doesn't already exist
def create_database(spark, db_name):
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {db_name}")

# Helper function to generate schema DDL from a list of fields
def get_schema_ddl(fields):
    return ", ".join([f"{f['name']} {f['type']}" for f in fields])

# Function to create an Iceberg table with the given schema and partitioning
def create_iceberg_table(spark, db_name, table_name, table_config):
    fields = table_config.get("table_schema", [])
    partition_cols = table_config.get("partition_by", [])

    schema_ddl = ", ".join([f"{f['name']} {f['type']}" for f in fields])
    partition_ddl = ", ".join(partition_cols)

    create_stmt = f"""
    CREATE TABLE IF NOT EXISTS {db_name}.{table_name} (
        {schema_ddl}
    )
    USING ICEBERG
    PARTITIONED BY ({partition_ddl})
    """
    spark.sql(create_stmt)

def load_raw_to_bronze(spark, table_config, storage_config):
    db = table_config['database']
    bronze_config = table_config["table_config"]["bronze"]
    table = bronze_config["table_name"]
    schema_ddl = get_schema_ddl(storage_config["raw_data_schema"])

    df = spark.read \
        .format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .schema(schema_ddl) \
        .load(f"gs://{storage_config['warehouse_bucket']}/{storage_config['raw_data_path']}/")

    # Adding new partitioned date column for table partitioning
    final_df = df.withColumn("InvoiceTimestamp", to_timestamp("InvoiceDate", "dd-MM-yyyy H.mm")) \
        .withColumn("partition_date", to_date("InvoiceTimestamp"))

    print("Create Iceberg table if not exist....")
    create_iceberg_table(spark, db, table, bronze_config)

    print(f"writing into Iceberg table - {db}.{table}")
    final_df.write \
    .mode("overwrite") \
    .partitionBy(bronze_config.get("partition_by", None)) \
    .format("iceberg") \
    .save(f"{db}.{table}")

def cleanse_and_load_to_silver(spark, table_config, storage_config):
    bronze_config = table_config["table_config"]["bronze"]
    table = bronze_config["table_name"]
    schema_ddl = get_schema_ddl(storage_config["raw_data_schema"])

    db = table_config['database']
    bronze_config = table_config["table_config"]["bronze"]
    silver_config = table_config["table_config"]["silver"]
    bronze_table = bronze_config["table_name"]
    silver_table = silver_config["table_name"]

    df = spark.read.table(f"{db}.{bronze_table}")

    # Remove rows with null Quantity or UnitPrice
    df_clean = df.dropna(subset=["Quantity", "UnitPrice"])

    # Keep only rows where Quantity is integer and UnitPrice is float-compatible
    df_clean = df_clean.filter(
                    col("Quantity").cast("int").isNotNull() &
                    col("UnitPrice").cast("double").isNotNull()
                )

    df_final = df_clean.withColumn("year", year("InvoiceTimestamp")) \
                .withColumn("month", month("InvoiceTimestamp")) \
                .withColumn("day", dayofmonth("InvoiceTimestamp"))

    print(f"writing into Iceberg table - {db}.{silver_table}")
    create_iceberg_table(spark, db, silver_table, silver_config)
    df_final.writeTo(f"{db}.{silver_table}").overwritePartitions()

def aggregate_and_load_to_gold(spark, table_config, storage_config):
    db = table_config['database']
    bronze_config = table_config["table_config"]["bronze"]
    silver_config = table_config["table_config"]["silver"]
    gold_config = table_config["table_config"]["gold"]

    bronze_table = bronze_config["table_name"]
    silver_table = silver_config["table_name"]
    gold_table = gold_config["table_name"]

    df = spark.read.table(f"{db}.{silver_table}")

    # Aggregate
    agg_df = df.groupBy("year", "month").agg(
            _sum(col("Quantity")).alias("total_quantity"),
            _sum(col("UnitPrice") * col("Quantity")).alias("total_revenue"),
                _count("InvoiceNo").alias("num_orders")
            )

    print(f"writing into Iceberg table - {db}.{gold_table}")
    create_iceberg_table(spark, db, gold_table, gold_config)
    agg_df.writeTo(f"{db}.{gold_table}").overwritePartitions()

def download_from_gcs(gcs_config_path):
    """
    Downloads a file from Google Cloud Storage (GCS) and returns its content as text.
    Args:
        gcs_config_path (str): The GCS path to the file (e.g., gs://bucket_name/path/to/file).
    Returns:
        str: The content of the file as a string.
    """
    client = storage.Client()
    parsed_url = urlparse(gcs_config_path)
    gcs_bucket_name = parsed_url.netloc  # Extract bucket name from the GCS URL
    gcs_blob_path = parsed_url.path[1:]  # Extract the file path within the bucket
    bucket = client.bucket(gcs_bucket_name)
    return bucket.blob(gcs_blob_path).download_as_text()

def get_metastore_uri(project_id, location, service_id):
    """
    Retrieves the endpoint URI of a Dataproc Metastore service.
    Args:
        project_id (str): The GCP project ID.
        location (str): The region where the Metastore service is located.
        service_id (str): The ID of the Metastore service.
    Returns:
        str: The endpoint URI of the Metastore service.
    """
    client = metastore_v1.DataprocMetastoreClient()
    service_name = f"projects/{project_id}/locations/{location}/services/{service_id}"
    service = client.get_service(name=service_name)
    return service.endpoint_uri

def export_to_biglake_parquet(spark, table_config, storage_config):
    db = table_config['database']
    gold_config = table_config["table_config"]["gold"]
    gold_table = gold_config["table_name"]
    biglake_path = f"gs://{storage_config['warehouse_bucket']}/{storage_config['bigquery_external_table_path']}"

    df = spark.read.table(f"{db}.{gold_table}")

    print(f"Exporting {db}.{gold_table} to BigLake Parquet at {biglake_path}")
    df.write.mode("overwrite").parquet(biglake_path)
    print("Export completed successfully.")

def main(config_path: str = None):
    # Load the configuration file from GCS
    config = yaml.safe_load(download_from_gcs(gcs_config_path=config_path))
    if not config:
        raise ValueError("Configuration could not be loaded. Please check the GCS path and file.")

    gcp_config = config['gcp']
    # dataproc_config = config['dataproc']
    storage_config = config['storage']
    table_config = config['iceberg']

    metastore_uri=get_metastore_uri(
        project_id=gcp_config['project_id'],
        location=gcp_config['region'],
        service_id=gcp_config['metastore_name']
        )
    print(f"Using Metastore URI: {metastore_uri}")
    spark = get_spark_session(metastore_uri=metastore_uri, warehouse_bucket=storage_config['warehouse_bucket'])

    # Create database if not exists
    create_database(spark, db_name=table_config['database'])

    # Load data into Bronze, Silver, and Gold layers
    print("Starting data processing pipeline...")
    print(f"Using Metastore URI: {metastore_uri}")
    print(f"Using Warehouse Bucket: {storage_config['warehouse_bucket']}")
    print(f"Using Database: {table_config['database']}")
    load_raw_to_bronze(spark, table_config, storage_config)
    cleanse_and_load_to_silver(spark, table_config, storage_config)
    aggregate_and_load_to_gold(spark, table_config, storage_config)
    export_to_biglake_parquet(spark, table_config, storage_config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spark Job Arguments")
    parser.add_argument("--input_config_path", required=True, help="GCS input path")
    args = parser.parse_args()
    main(args.input_config_path)
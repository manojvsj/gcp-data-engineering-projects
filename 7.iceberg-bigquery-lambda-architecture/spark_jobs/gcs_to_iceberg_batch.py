#!/usr/bin/env python3
"""
Simple Batch Job: Load GCS Files into Iceberg
Reads JSON files from GCS and writes to Iceberg table
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import sys
import yaml

def load_config(config_path):
    """Load configuration from config file path (local or GCS)"""
    import os
    from google.cloud import storage
    
    # Check if it's a GCS path
    if config_path.startswith('gs://'):
        # Parse GCS path: gs://bucket/path/file
        path_parts = config_path[5:].split('/', 1)  # Remove 'gs://' and split
        bucket_name = path_parts[0]
        blob_path = path_parts[1] if len(path_parts) > 1 else 'config.yaml'
        
        try:
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            
            config_content = blob.download_as_text()
            return yaml.safe_load(config_content)
            
        except Exception as e:
            print(f"❌ Failed to load config from GCS: {e}")
            raise e
    else:
        # Local file path
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"❌ Failed to load config from local file: {e}")
            raise e

def create_spark_session(warehouse_path):
    """Create Spark session with Iceberg support"""
    return SparkSession.builder \
        .appName("GCS-to-Iceberg-Batch") \
        .config("spark.sql.warehouse.dir", warehouse_path) \
        .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.spark_catalog.type", "hive") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .enableHiveSupport() \
        .getOrCreate()


def process_date_files(spark, gcs_path, target_date):
    """Simple: Read JSON files for specific date"""
    
    date_path = f"{gcs_path}/{target_date}/*.json"
    print(f"📂 Reading files for date {target_date}: {date_path}")
    
    try:
        # Read JSON files for specific date
        df = spark.read.json(date_path)
        
        count = df.count()
        print(f"📊 Found {count} records for {target_date}")
        
        if count == 0:
            print(f"ℹ️  No files found for date: {target_date}")
            return None
            
        # Show sample data
        print("🔍 Sample data:")
        df.show(3, truncate=False)
        
        # Simple transformation: create properties_json from individual fields
        processed_df = df.select(
            col("event_id"),
            col("event_type"), 
            col("user_id"),
            col("session_id"),
            col("event_timestamp").cast("timestamp"),
            # Create JSON from properties
            to_json(struct(
                col("product"),
                col("price"),
                col("quantity"), 
                col("country"),
                col("device_type"),
                col("page_url"),
                col("referrer")
            )).alias("properties_json"),
            col("data_source"),
            col("schema_version"),
            col("processing_timestamp").cast("timestamp"),
            # Add event_date
            lit(target_date).cast("date").alias("event_date")
        )
        
        return processed_df
        
    except Exception as e:
        print(f"❌ Error reading files for {target_date}: {e}")
        return None

def save_to_iceberg(df, database_name, table_name):
    """Simple: Save data to Iceberg table"""
    
    table_name_full = f"{database_name}.{table_name}"
    
    if df is None or df.count() == 0:
        print("ℹ️  No records to save")
        return
    
    print(f"💾 Saving {df.count()} records to: {table_name_full}")
    
    try:
        # Simple write to Iceberg table
        df.writeTo(table_name_full).append()
        print(f"✅ Successfully saved to {table_name_full}")
        
    except Exception as e:
        print(f"❌ Failed to save to Iceberg: {e}")
        raise e


def main(config_path, target_date):
    """Simple main function - process specific date"""
    
    config = load_config(config_path)
    
    # Get paths from config
    warehouse_path = f"gs://{config['iceberg']['warehouse']}/warehouse"
    database_name = config['iceberg']['database']
    table_name = config['iceberg']['table']
    gcs_path = f"gs://{config['gcs']['temp_bucket']}/iceberg-staging/events"
    
    print("🚀 SIMPLE BATCH JOB: GCS → ICEBERG")
    print(f"📅 Processing date: {target_date}")
    print(f"📂 Reading from: {gcs_path}/{target_date}/")
    print(f"💾 Writing to: {database_name}.{table_name}")
    print()
    
    # Create Spark session
    spark = create_spark_session(warehouse_path)
    
    try:
        # Step 1: Read files for specific date
        df = process_date_files(spark, gcs_path, target_date)
        
        # Step 2: Save to Iceberg (only if we have data)
        if df is not None:
            save_to_iceberg(df, database_name, table_name)
            print(f"✅ Processed {df.count()} records for {target_date}")
        else:
            print(f"ℹ️  No data to process for {target_date}")
        
        # Step 3: Show total in table
        result = spark.sql(f"SELECT COUNT(*) as total FROM {database_name}.{table_name}")
        result.show()
        
        print("✅ Job completed!")
        
    except Exception as e:
        print(f"❌ Job failed: {e}")
        raise e
        
    finally:
        spark.stop()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: gcs_to_iceberg_batch.py <config_file_path> <date>")
        print("Example: gcs_to_iceberg_batch.py gs://bucket/config.yaml 2024-01-01")
        print("Example: gcs_to_iceberg_batch.py /path/to/config.yaml 2024-01-01")
        sys.exit(1)
    
    config_path = sys.argv[1]
    target_date = sys.argv[2]
    
    main(config_path, target_date)
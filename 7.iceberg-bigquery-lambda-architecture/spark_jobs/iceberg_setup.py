from pyspark.sql import SparkSession
import sys

def main(warehouse_path, database_name, table_name):
    try:
        spark = SparkSession.builder \
            .appName("iceberg-table-setup") \
            .config("spark.sql.warehouse.dir", warehouse_path) \
            .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog") \
            .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
            .config("spark.sql.catalog.spark_catalog.type", "hive") \
            .enableHiveSupport() \
            .getOrCreate()

            # List databases from metastore
        spark.sql("SHOW DATABASES").show()

        print(f"\n📁 Creating database: {database_name}")
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        spark.sql(f"USE {database_name}")
        print(f"✅ Database {database_name} ready")

        # Show existing tables in database
        print(f"\n📋 Current tables in {database_name}:")
        existing_tables = spark.sql("SHOW TABLES")
        existing_tables.show()

        # Create Iceberg table for streaming events
        print(f"\n🏗️  Creating Iceberg table: {database_name}.{table_name}")

        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {database_name}.{table_name} (
            event_id STRING COMMENT 'Unique identifier for the event',
            event_type STRING COMMENT 'Type of event (e.g., purchase, click, view)',
            user_id STRING COMMENT 'User identifier',
            session_id STRING COMMENT 'Session identifier',
            event_timestamp TIMESTAMP COMMENT 'When the event occurred',
            properties_json STRING COMMENT 'JSON string of additional event properties',
            data_source STRING COMMENT 'Source system that generated the event',
            schema_version STRING COMMENT 'Schema version for compatibility',
            processing_timestamp TIMESTAMP COMMENT 'When the event was processed',
            event_date DATE COMMENT 'Date partition column'
        )
        USING ICEBERG
        PARTITIONED BY (event_date)
        TBLPROPERTIES (
            'write.format.default' = 'parquet',
            'write.parquet.compression-codec' = 'snappy',
            'write.metadata.delete-after-commit.enabled' = 'true',
            'write.metadata.previous-versions-max' = '5'
        )
        """

        print("📝 Executing CREATE TABLE statement...")
        spark.sql(create_table_sql)
        print(f"✅ Table {database_name}.{table_name} created successfully")

            # Describe the table to verify structure
        print(f"\n📊 Table structure for {database_name}.{table_name}:")
        table_desc = spark.sql(f"DESCRIBE EXTENDED {database_name}.{table_name}")
        table_desc.show(50, truncate=False)
        # Insert test data to verify everything works
        print(f"\n🧪 Inserting test data into {database_name}.{table_name}")

        sample_data_sql = f"""
        INSERT INTO {database_name}.{table_name} VALUES
        (
            'test_event_001',
            'purchase',
            'user_123',
            'session_456',
            TIMESTAMP '2024-01-01 10:00:00',
            '{{"product": "laptop", "price": 999.99, "category": "electronics"}}',
            'serverless_setup',
            '1.0',
            TIMESTAMP '2024-01-01 10:01:00',
            DATE '2024-01-01'
        ),
        (
            'test_event_002',
            'view',
            'user_456',
            'session_789',
            TIMESTAMP '2024-01-01 11:30:00',
            '{{"page": "/products", "referrer": "google"}}',
            'serverless_setup',
            '1.0',
            TIMESTAMP '2024-01-01 11:31:00',
            DATE '2024-01-01'
        ),
        (
            'test_event_003',
            'click',
            'user_789',
            'session_123',
            TIMESTAMP '2024-01-02 14:15:00',
            '{{"button": "add_to_cart", "product_id": "prod_456"}}',
            'serverless_setup',
            '1.0',
            TIMESTAMP '2024-01-02 14:16:00',
            DATE '2024-01-02'
        )
        """

        spark.sql(sample_data_sql)
        print("✅ Test data inserted successfully")

        # Query the data back to verify
        print(f"\n📈 Sample data in {database_name}.{table_name}:")
        result = spark.sql(f"SELECT * FROM {database_name}.{table_name} ORDER BY event_timestamp")
        result.show(10, truncate=False)

        # Show table statistics
        print(f"\n📊 Table statistics:")
        count_result = spark.sql(f"SELECT COUNT(*) as total_events FROM {database_name}.{table_name}")
        count_result.show()

        # Show partition information
        print(f"\n🗂️  Partition information:")
        partition_result = spark.sql(f"SELECT event_date, COUNT(*) as events_count FROM {database_name}.{table_name} GROUP BY event_date ORDER BY event_date")
        partition_result.show()

        # Show Iceberg table metadata
        print(f"\n🔍 Iceberg table metadata:")
        metadata_result = spark.sql(f"SELECT * FROM {database_name}.{table_name}.snapshots")
        metadata_result.show(truncate=False)

        print("\n" + "=" * 60)
        print("🎉 Serverless Iceberg setup completed successfully!")
        print("=" * 60)
        print("✅ Database created")
        print("✅ Iceberg table created with partitioning")
        print("✅ Test data inserted and verified")
        print("✅ Table is ready for streaming data")

    except Exception as e:
        print(f"\n❌ Error during Iceberg setup: {e}")
        print("Stack trace:")
        import traceback
        traceback.print_exc()
        raise e

    finally:
        print(f"\n🔄 Closing Spark session...")
        spark.stop()
        print("✅ Spark session closed")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: main.py <warehouse_path> <database_name> <table_name>")
        sys.exit(1)

    warehouse_path = sys.argv[1]
    database_name = sys.argv[2]
    table_name = sys.argv[3]

    main(warehouse_path, database_name, table_name)
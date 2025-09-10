from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum as spark_sum, avg, max as spark_max, min as spark_min, desc
import sys

def create_spark_session(warehouse_path):
    """Initialize Spark session with Iceberg configurations for GCP"""
    return SparkSession.builder \
        .appName("simple-iceberg-batch-analysis") \
        .config("spark.sql.warehouse.dir", warehouse_path) \
        .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.spark_catalog.type", "hive") \
        .enableHiveSupport() \
        .getOrCreate()

def basic_statistics(spark, database_name, table_name):
    """Generate basic aggregations for the events table"""
    print("\n📊 BASIC STATISTICS")
    print("=" * 40)

    # Load data from Iceberg table
    df = spark.sql(f"SELECT * FROM {database_name}.{table_name}")

    # Basic counts
    total_events = df.count()
    unique_users = df.select("user_id").distinct().count()
    unique_sessions = df.select("session_id").distinct().count()

    print(f"Total Events: {total_events:,}")
    print(f"Unique Users: {unique_users:,}")
    print(f"Unique Sessions: {unique_sessions:,}")

    # Event type distribution
    print("\n📋 Event Types:")
    df.groupBy("event_type") \
        .agg(count("*").alias("count")) \
        .orderBy(desc("count")) \
        .show()

    # Daily event counts
    print("� Events by Date:")
    df.groupBy("event_date") \
        .agg(count("*").alias("events_per_day")) \
        .orderBy("event_date") \
        .show()

    return df

def user_analysis(df):
    """Analyze user behavior with simple aggregations"""
    print("\n👤 USER ANALYSIS")
    print("=" * 40)

    # Events per user
    user_stats = df.groupBy("user_id") \
        .agg(count("*").alias("total_events")) \
        .orderBy(desc("total_events"))

    print("� Top 10 Most Active Users:")
    user_stats.limit(10).show()

    # User activity summary
    print("📊 User Activity Summary:")
    user_stats.agg(
        avg("total_events").alias("avg_events_per_user"),
        spark_max("total_events").alias("max_events_per_user"),
        spark_min("total_events").alias("min_events_per_user")
    ).show()

def session_analysis(df):
    """Analyze session patterns"""
    print("\n🔗 SESSION ANALYSIS")
    print("=" * 40)

    # Events per session
    session_stats = df.groupBy("session_id") \
        .agg(count("*").alias("events_in_session")) \
        .orderBy(desc("events_in_session"))

    print("� Session Statistics:")
    session_stats.agg(
        avg("events_in_session").alias("avg_events_per_session"),
        spark_max("events_in_session").alias("max_events_per_session"),
        spark_min("events_in_session").alias("min_events_per_session")
    ).show()

    print("� Top 10 Longest Sessions:")
    session_stats.limit(10).show()

def main(warehouse_path, database_name, table_name):
    """Main function to run simple batch analysis"""
    try:
        print("🚀 Starting Simple Iceberg Batch Analysis")
        print("=" * 60)

        # Create Spark session
        spark = create_spark_session(warehouse_path)

        # Set database context
        spark.sql(f"USE {database_name}")

        # Run basic analysis
        print(f"📊 Analyzing table: {database_name}.{table_name}")
        df = basic_statistics(spark, database_name, table_name)

        # Cache for better performance
        df.cache()

        # Run user analysis
        user_analysis(df)

        # Run session analysis
        session_analysis(df)

        print("\n✅ Analysis Complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise e

    finally:
        spark.stop()
        print("🔄 Spark session closed")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python batch_analysis.py <warehouse_path> <database_name> <table_name>")
        print("Example: python batch_analysis.py /tmp/iceberg-warehouse analytics_db events")
        sys.exit(1)

    warehouse_path = sys.argv[1]
    database_name = sys.argv[2]
    table_name = sys.argv[3]

    main(warehouse_path, database_name, table_name)

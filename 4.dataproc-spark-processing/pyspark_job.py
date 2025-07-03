from pyspark.sql import SparkSession
from pyspark.sql.functions import to_date, to_timestamp
import argparse



def main(input_path:str, output_path:str):
    print("hello")
    spark = SparkSession.builder \
    .appName("transformation") \
    .getOrCreate()

    schema_ddl = """
    InvoiceNo INT,
    StockCode STRING,
    Description STRING,
    Quantity INT,
    InvoiceDate STRING,
    UnitPrice FLOAT,
    CustomerID STRING,
    Country STRING"""

    df = spark.read \
        .format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .schema(schema_ddl) \
        .load(input_path)

    print("df is created")

    # Adding new partitioned date column for table partitioning
    final_df = df.withColumn("InvoiceTimestamp", to_timestamp("InvoiceDate", "dd-MM-yyyy H.mm")) \
       .withColumn("partition_date", to_date("InvoiceTimestamp"))

    print("writing into gcs location")
    # writing into GCS output bucket as parquet format
    final_df.write \
    .mode("overwrite") \
    .partitionBy("partition_date") \
    .format("parquet") \
    .save(output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spark Job Arguments")
    parser.add_argument("--input_path", required=True, help="GCS input path")
    parser.add_argument("--output_path", required=True, help="GCS output path")

    args = parser.parse_args()
    main(args.input_path, args.output_path)
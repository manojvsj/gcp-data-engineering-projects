CREATE OR REPLACE EXTERNAL TABLE `<project-name>.biglake_sales.sales`
with partition columns (partition_date date)
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://dataproc-learning-adsf/output/sales_partitioned/*'],
  hive_partition_uri_prefix = 'gs://dataproc-learning-adsf/output/sales_partitioned/'
  )

-- Get the count of each partition
-- select partition_date, count(*) as row_count from `<project-name>.biglake_sales.sales` group by partition_date
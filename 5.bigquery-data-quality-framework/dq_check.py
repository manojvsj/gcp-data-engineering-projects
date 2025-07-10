import yaml  # For reading the config file
from google.cloud import bigquery
from datetime import datetime

client = bigquery.Client()
PROJECT_ID="your project name"
DATASET="data_quality"

def load_config(path="dq-config.yaml"):
    # Loads table/check info from YAML file
    with open(path, "r") as f:
        return yaml.safe_load(f)

def run_check(table, check):
    table_name = table["name"]
    col = check["column"]
    check_type = check["type"]
    partition_col = table.get("partition_column")

    # Only run check on today's partition (if defined)
    if partition_col:
        date_filter = f"DATE({partition_col}) = CURRENT_DATE()"
    else:
        date_filter = "1=1"  # fallback: no filter

    # Count total rows to get pass ratio
    total_query = f"SELECT COUNT(*) FROM `{table_name}` WHERE {date_filter}"
    total_rows = client.query(total_query).result().to_dataframe().iloc[0, 0]
    print(f"{total_query} - {total_rows}")

    # Build query depending on check type
    print(f"Validating {check_type.upper()} .......")
    if check_type == "null_check":
        query = f"SELECT COUNT(*) FROM `{table_name}` WHERE {date_filter} AND {col} IS NULL"

    elif check_type == "duplicate_check":
        query = f"""
        SELECT COUNT(*) FROM (
          SELECT {col}, COUNT(*) c FROM `{table_name}`
          WHERE {date_filter}
          GROUP BY {col} HAVING c > 1
        )
        """

    elif check_type == "range_check":
        min_val = check["min"]
        max_val = check["max"]
        query = f"SELECT COUNT(*) FROM `{table_name}` WHERE {date_filter} AND ({col} < {min_val} OR {col} > {max_val})"

    else:
        print(f"Unsupported check type: {check_type}")
        return

    # Run the DQ check query

    failed_rows = client.query(query).result().to_dataframe().iloc[0, 0]
    pass_ratio = (total_rows - failed_rows) / total_rows if total_rows else 0
    print("...")
    print(f"Inserting {check_type} results into {PROJECT_ID}.{DATASET}.data_quality_results ...")
    print(f"{check_type.upper()} pass ratio - {pass_ratio}")
    # Write result to monitoring table
    monitoring_query = f"""
    INSERT INTO `{PROJECT_ID}.{DATASET}.data_quality_results`
    (partition_date, check_name, table_name, failed_rows, total_rows, pass_ratio, checked_at)
    VALUES (
        CURRENT_DATE(),
      "{check_type}_{col}",
      "{table_name}",
      {failed_rows},
      {total_rows},
      {pass_ratio},
      TIMESTAMP("{datetime.utcnow()}")
    )
    """
    client.query(monitoring_query).result()

def run_dq_checks():
    config = load_config()
    for table in config["tables"]:
        for check in table["checks"]:
            run_check(table, check)

if __name__ == "__main__":
    run_dq_checks()

def create_bq_table(dataset_id, table_id, schema):
    from google.cloud import bigquery

    client = bigquery.Client()
    table_ref = client.dataset(dataset_id).table(table_id)
    table = bigquery.Table(table_ref, schema=schema)
    table = client.create_table(table)
    return table


def query_bq_table(query):
    from google.cloud import bigquery

    client = bigquery.Client()
    query_job = client.query(query)
    results = query_job.result()
    return results


def delete_bq_table(dataset_id, table_id):
    from google.cloud import bigquery

    client = bigquery.Client()
    table_ref = client.dataset(dataset_id).table(table_id)
    client.delete_table(table_ref)
    return f"Deleted table {table_ref}"
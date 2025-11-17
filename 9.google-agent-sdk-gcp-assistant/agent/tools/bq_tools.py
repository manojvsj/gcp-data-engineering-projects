from typing import Dict, Any
from google.cloud import bigquery

client = bigquery.Client()

def _safe_list_datasets(project_id: str):
    return [d.dataset_id for d in client.list_datasets(project=project_id)]

def _safe_list_tables(project_id: str, dataset_id: str):
    dataset_ref = f"{project_id}.{dataset_id}"
    return [t.table_id for t in client.list_tables(dataset_ref)]

def _safe_get_table_schema(project_id: str, dataset_id: str, table_id: str):
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    table = client.get_table(table_ref)
    return [{"name": f.name, "type": f.field_type, "mode": f.mode} for f in table.schema]

# ADK expects plain callable tools; return dicts so the agent can present them
def list_datasets(project_id: str) -> Dict[str, Any]:
    """List BigQuery datasets in a project."""
    try:
        datasets = _safe_list_datasets(project_id)
        return {"status": "ok", "project_id": project_id, "datasets": datasets}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def list_tables(project_id: str, dataset_id: str) -> Dict[str, Any]:
    """List tables in a dataset."""
    try:
        tables = _safe_list_tables(project_id, dataset_id)
        return {"status": "ok", "project_id": project_id, "dataset_id": dataset_id, "tables": tables}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def get_table_schema(project_id: str, dataset_id: str, table_id: str) -> Dict[str, Any]:
    """Return BigQuery table schema."""
    try:
        schema = _safe_get_table_schema(project_id, dataset_id, table_id)
        return {"status": "ok", "project_id": project_id, "dataset_id": dataset_id, "table_id": table_id, "schema": schema}
    except Exception as e:
        return {"status": "error", "error": str(e)}

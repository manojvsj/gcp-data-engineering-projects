from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import bigquery
import os
import json

app = FastAPI()

# Read configuration from environment variables
PROJECT_ID = os.getenv("PROJECT_ID", "")
DATASET_ID = os.getenv("DATASET_ID", "sales_data")
TABLE_ID = os.getenv("TABLE_ID", "orders")

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID if PROJECT_ID else None)


class QueryRequest(BaseModel):
    sql: str
    project_id: str = None


@app.get("/")
async def root():
    return {
        "status": "MCP BigQuery Server Running",
        "version": "1.0",
        "project_id": PROJECT_ID or "default",
        "dataset_id": DATASET_ID,
        "table_id": TABLE_ID,
    }


@app.post("/query_bigquery")
async def query_bigquery(request: QueryRequest):
    """
    Execute SQL query on BigQuery and return results
    """
    try:
        # Validate SQL query
        if not request.sql or not request.sql.strip():
            raise HTTPException(status_code=400, detail="SQL query is empty or missing")

        # Use project_id from request or fall back to environment variable
        project_id = request.project_id or PROJECT_ID

        # Execute query
        query_job = client.query(
            request.sql, project=project_id if project_id else None
        )
        results = query_job.result()

        # Convert results to list of dicts
        rows = []
        for row in results:
            rows.append(dict(row))

        return {"success": True, "data": rows, "row_count": len(rows)}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/config")
async def get_config():
    """
    Return current configuration (for debugging)
    """
    return {
        "project_id": PROJECT_ID or "not set",
        "dataset_id": DATASET_ID,
        "table_id": TABLE_ID,
        "full_table_name": (
            f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
            if PROJECT_ID
            else f"{DATASET_ID}.{TABLE_ID}"
        ),
    }

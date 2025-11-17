from typing import Dict, Any
from google.cloud import storage

client = storage.Client()

def list_buckets(project_id: str) -> Dict[str, Any]:
    """List GCS buckets in a project."""
    try:
        buckets = [b.name for b in client.list_buckets(project=project_id)]
        return {"status": "ok", "project_id": project_id, "buckets": buckets}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def list_files(bucket_name: str, prefix: str = "") -> Dict[str, Any]:
    """List files in a GCS bucket (optional prefix)."""
    try:
        bucket = client.bucket(bucket_name)
        blobs = list(bucket.list_blobs(prefix=prefix))
        files = [b.name for b in blobs]
        return {"status": "ok", "bucket": bucket_name, "prefix": prefix, "files": files}
    except Exception as e:
        return {"status": "error", "error": str(e)}

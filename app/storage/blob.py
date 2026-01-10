import os
import uuid
from azure.storage.blob import BlobServiceClient

# 🔹 THIS IS WHERE os.getenv IS USED
def get_blob_client():
    conn_str = os.getenv("AZURE_BLOB_CONN") or os.getenv("azure-blob-conn")
    if not conn_str:
        return None
    return BlobServiceClient.from_connection_string(conn_str)

def upload_evidence(file_bytes: bytes, filename: str, content_type: str) -> str:
    """
    Upload evidence to Azure Blob Storage.
    Returns the blob URL.
    """
    client = get_blob_client()
    if not client:
        # Fail gracefully if called without configuration
        raise RuntimeError("AZURE_BLOB_CONN environment variable is not set")

    container_name = "evidence"
    blob_name = f"{uuid.uuid4()}-{filename}"

    blob_client = client.get_blob_client(
        container=container_name,
        blob=blob_name
    )

    blob_client.upload_blob(
        file_bytes,
        overwrite=False,
        content_type=content_type
    )

    return blob_client.url
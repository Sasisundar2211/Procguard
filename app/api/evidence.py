from fastapi import APIRouter, UploadFile, File
from app.storage.blob import upload_evidence

router = APIRouter()

@router.post("/evidence/upload")
async def upload(file: UploadFile = File(...)):
    data = await file.read()

    blob_url = upload_evidence(
        file_bytes=data,
        filename=file.filename,
        content_type=file.content_type
    )

    # Store blob_url in PostgreSQL (separate module)
    return {"blob_url": blob_url}
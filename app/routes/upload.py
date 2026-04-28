from fastapi import APIRouter, UploadFile
import shutil
import os
from app.rag.ingest import ingest_pdf

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile):

    os.makedirs("data", exist_ok=True)

    file_path = f"data/{file.filename}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    ingest_pdf(file_path)

    return {"message": "File uploaded successfully"}
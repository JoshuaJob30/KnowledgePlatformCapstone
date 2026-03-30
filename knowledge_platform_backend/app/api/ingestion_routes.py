# app/api/ingestion_routes.py
from fastapi import APIRouter, UploadFile, File, Request, HTTPException
from app.services import ingestion_service
from app.core.logging import logger
import os

router = APIRouter()

@router.post("/upload")
async def upload_documents(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        filepath = ingestion_service.save_file(file.filename, await file.read())
        num_chunks = ingestion_service.ingest_and_index(filepath, file.filename)
        results.append({
            "filename": file.filename,
            "stored_at": filepath,
            "chunks_ingested": num_chunks
        })
    return {"results": results}


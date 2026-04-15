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

@router.post("/clear_docs")
async def clear_docs_route():
    try:
        ingestion_service.clear_docs()
        return {"status": "success", "message": "Uploaded documents cleared."}
    except Exception as e:
        logger.error(f"[Docs] Error clearing documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing docs: {e}")
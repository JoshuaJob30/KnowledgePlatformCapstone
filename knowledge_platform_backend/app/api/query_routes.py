# app/api/query_routes.py
from fastapi import APIRouter, Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.services.agent_service import answer_query
from app.core.logging import logger

router = APIRouter()

# Configure limiter
limiter = Limiter(key_func=get_remote_address)

@router.get("")
@router.get("/")
@limiter.limit("60/minute")  # allow 60 queries per minute per client IP
async def query_document(request: Request, q: str):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    result = await answer_query(q)
    return {"query": q, "answer": result["answer"], "source": result["source"]}

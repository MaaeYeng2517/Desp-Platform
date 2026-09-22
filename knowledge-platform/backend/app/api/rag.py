"""RAG API endpoints"""
from fastapi import APIRouter, HTTPException
from typing import List

from backend.app.schemas import RAGRequest, RAGResponse

router = APIRouter()


@router.post("/", response_model=RAGResponse)
async def rag_query(request: RAGRequest):
    """Generate answer using RAG"""
    from backend.app.services.rag import rag_engine
    
    kb_ids_str = [str(kb_id) for kb_id in request.kb_ids]
    
    result = await rag_engine.answer(
        request.query,
        kb_ids_str,
        request.metadata_filters,
        request.limit,
        request.temperature,
        request.max_tokens
    )
    
    return result
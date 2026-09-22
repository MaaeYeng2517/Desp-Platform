"""Search API endpoints"""
from fastapi import APIRouter, HTTPException
from typing import List

from backend.app.schemas import SearchRequest, SearchResponse

router = APIRouter()


@router.post("/", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Perform hybrid search"""
    from backend.app.services.retrieval import retrieval_engine
    
    kb_ids_str = [str(kb_id) for kb_id in request.kb_ids]
    
    result = await retrieval_engine.search(
        request.query,
        kb_ids_str,
        request.metadata_filters,
        request.limit,
        request.search_type
    )
    
    return result


@router.post("/keyword")
async def keyword_search(query: str, limit: int = 10):
    """Keyword-only search"""
    from backend.app.services.retrieval import retrieval_engine
    
    results = await retrieval_engine.keyword_search(query, limit)
    return {"results": results, "total": len(results)}


@router.post("/vector")
async def vector_search(query: str, limit: int = 10):
    """Vector-only search"""
    from backend.app.services.retrieval import retrieval_engine
    
    results = await retrieval_engine.vector_search(query, limit)
    return {"results": results, "total": len(results)}


@router.post("/graph")
async def graph_search(query: str, limit: int = 10):
    """Graph-based search"""
    from backend.app.services.retrieval import retrieval_engine
    
    results = await retrieval_engine.graph_search(query, limit)
    return {"results": results, "total": len(results)}
"""Knowledge Bases API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime

from backend.app.schemas import KnowledgeBaseCreate, KnowledgeBaseResponse

router = APIRouter()

# In-memory storage
_kbs = {}
_kb_id_counter = 1


@router.post("/", response_model=KnowledgeBaseResponse)
async def create_kb(kb: KnowledgeBaseCreate):
    """Create a new knowledge base"""
    global _kb_id_counter
    
    kb_id = f"kb_{_kb_id_counter}"
    _kb_id_counter += 1
    
    new_kb = {
        "id": kb_id,
        "tenant_id": "t_1",
        "owner_id": "u_1",
        "name": kb.name,
        "description": kb.description,
        "slug": kb.slug or kb.name.lower().replace(" ", "-"),
        "settings": kb.settings,
        "is_published": False,
        "status": "draft",
        "version": "1.0",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    _kbs[kb_id] = new_kb
    return new_kb


@router.get("/", response_model=List[KnowledgeBaseResponse])
async def list_kbs():
    """List all knowledge bases"""
    return list(_kbs.values())


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_kb(kb_id: str):
    """Get knowledge base by ID"""
    if kb_id not in _kbs:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return _kbs[kb_id]


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_kb(kb_id: str, kb: KnowledgeBaseCreate):
    """Update knowledge base"""
    if kb_id not in _kbs:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    _kbs[kb_id].update({
        "name": kb.name,
        "description": kb.description,
        "slug": kb.slug or kb.name.lower().replace(" ", "-"),
        "settings": kb.settings,
        "updated_at": datetime.utcnow()
    })
    
    return _kbs[kb_id]


@router.delete("/{kb_id}")
async def delete_kb(kb_id: str):
    """Delete knowledge base"""
    if kb_id not in _kbs:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    del _kbs[kb_id]
    return {"message": "Knowledge base deleted"}


@router.post("/{kb_id}/publish")
async def publish_kb(kb_id: str):
    """Publish knowledge base"""
    if kb_id not in _kbs:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    _kbs[kb_id]["is_published"] = True
    _kbs[kb_id]["status"] = "published"
    
    return {"message": "Knowledge base published", "kb_id": kb_id}
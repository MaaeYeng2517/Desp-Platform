"""Documents API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from datetime import datetime

from backend.app.schemas import DocumentCreate, DocumentResponse

router = APIRouter()

# In-memory storage
_documents = {}
_doc_id_counter = 1


@router.post("/", response_model=DocumentResponse)
async def create_document(doc: DocumentCreate):
    """Create a new document"""
    global _doc_id_counter
    
    doc_id = f"doc_{_doc_id_counter}"
    _doc_id_counter += 1
    
    new_doc = {
        "id": doc_id,
        "kb_id": doc.kb_id,
        "title": doc.title,
        "source_type": doc.source_type,
        "source_url": doc.source_url,
        "status": "pending",
        "version": "1.0",
        "is_published": False,
        "created_at": datetime.utcnow()
    }
    
    _documents[doc_id] = new_doc
    return new_doc


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), kb_id: str = None):
    """Upload a document file"""
    global _doc_id_counter
    
    doc_id = f"doc_{_doc_id_counter}"
    _doc_id_counter += 1
    
    # Read file content
    content = await file.read()
    
    new_doc = {
        "id": doc_id,
        "kb_id": kb_id or "kb_1",
        "title": file.filename,
        "source_type": "file",
        "source_url": None,
        "status": "processing",
        "version": "1.0",
        "is_published": False,
        "created_at": datetime.utcnow(),
        "file_size": len(content),
        "mime_type": file.content_type
    }
    
    _documents[doc_id] = new_doc
    
    # Process document
    from backend.app.services.ingestion import ingestion_engine
    from backend.app.services.processing import processing_engine
    
    # Extract text
    content_str = content.decode('utf-8', errors='ignore')
    result = await processing_engine.process(content_str, "file")
    
    # Update document with processed content
    _documents[doc_id]["status"] = "processed"
    _documents[doc_id]["content"] = result["extracted"]
    _documents[doc_id]["chunks"] = result["chunks"]
    _documents[doc_id]["entities"] = result["entities"]
    
    return new_doc


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(kb_id: str = None):
    """List documents, optionally filtered by knowledge base"""
    docs = list(_documents.values())
    if kb_id:
        docs = [d for d in docs if d["kb_id"] == kb_id]
    return docs


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str):
    """Get document by ID"""
    if doc_id not in _documents:
        raise HTTPException(status_code=404, detail="Document not found")
    return _documents[doc_id]


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Delete document"""
    if doc_id not in _documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    del _documents[doc_id]
    return {"message": "Document deleted"}
"""Pydantic schemas for API requests/responses"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class TenantCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    settings: Dict[str, Any] = {}


class TenantResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    settings: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    tenant_id: UUID


class UserResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    email: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    roles: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeBaseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    slug: Optional[str] = None
    settings: Dict[str, Any] = {}


class KnowledgeBaseResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    owner_id: UUID
    name: str
    description: Optional[str]
    slug: str
    settings: Dict[str, Any]
    is_published: bool
    status: str
    version: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentCreate(BaseModel):
    kb_id: UUID
    title: str
    source_type: str
    source_url: Optional[str] = None
    metadata: Dict[str, Any] = {}


class DocumentResponse(BaseModel):
    id: UUID
    kb_id: UUID
    title: str
    source_type: str
    source_url: Optional[str]
    status: str
    version: str
    is_published: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    content: str
    chunk_index: int
    token_count: Optional[int]
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    query: str
    kb_ids: List[UUID]
    metadata_filters: Optional[Dict[str, Any]] = None
    limit: int = 10
    score_threshold: Optional[float] = None
    search_type: str = "hybrid"  # keyword, vector, hybrid


class SearchResult(BaseModel):
    chunk_id: UUID
    document_id: UUID
    title: str
    content: str
    score: float
    metadata: Dict[str, Any]
    sources: List[str] = []


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int
    latency_ms: float


class RAGRequest(BaseModel):
    query: str
    kb_ids: List[UUID]
    metadata_filters: Optional[Dict[str, Any]] = None
    limit: int = 5
    temperature: float = 0.7
    max_tokens: int = 1000


class RAGResponse(BaseModel):
    answer: str
    sources: List[SearchResult]
    citations: List[Dict[str, Any]]
    latency_ms: float
    token_usage: Dict[str, int]


class WorkflowCreate(BaseModel):
    kb_id: UUID
    name: str
    description: Optional[str] = None
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []


class WorkflowResponse(BaseModel):
    id: UUID
    kb_id: UUID
    name: str
    description: Optional[str]
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    is_active: bool
    version: str
    
    class Config:
        from_attributes = True


class MetadataSchemaCreate(BaseModel):
    kb_id: UUID
    name: str
    description: Optional[str] = None
    fields: List[Dict[str, Any]]
    taxonomy: Dict[str, Any] = {}


class MetadataSchemaResponse(BaseModel):
    id: UUID
    kb_id: UUID
    name: str
    description: Optional[str]
    fields: List[Dict[str, Any]]
    taxonomy: Dict[str, Any]
    is_active: bool
    
    class Config:
        from_attributes = True


class EvaluationRequest(BaseModel):
    kb_id: UUID
    dataset_id: Optional[UUID] = None
    questions: Optional[List[Dict[str, Any]]] = None


class EvaluationResponse(BaseModel):
    run_id: UUID
    metrics: Dict[str, float]
    overall_score: float
    results: List[Dict[str, Any]]
    status: str
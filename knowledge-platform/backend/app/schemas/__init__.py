"""Pydantic schemas for API requests/responses"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import enum


class UserRole(str, enum.Enum):
    GUEST = "guest"
    MEMBER = "member"
    ADMIN = "admin"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    TRIALING = "trialing"
    PAUSED = "paused"


class ContactStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    SPAM = "spam"


class ApiKeyScope(str, enum.Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    SEARCH = "search"
    RAG = "rag"
    DOCUMENTS = "documents"
    WORKFLOWS = "workflows"


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
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = None
    tenant_id: Optional[UUID] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    email: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MembershipPlanCreate(BaseModel):
    stripe_price_id: Optional[str] = None
    stripe_product_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    price_cents: int = 0
    currency: str = "usd"
    interval: str = "month"
    api_calls_per_month: int = 1000
    features: List[str] = []
    is_active: bool = True
    sort_order: int = 0


class MembershipPlanResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    stripe_price_id: Optional[str]
    stripe_product_id: Optional[str]
    name: str
    description: Optional[str]
    price_cents: int
    currency: str
    interval: str
    api_calls_per_month: int
    features: List[str]
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionCreate(BaseModel):
    plan_id: UUID
    stripe_payment_method_id: Optional[str] = None


class SubscriptionResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    user_id: UUID
    plan_id: UUID
    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]
    stripe_price_id: Optional[str]
    status: SubscriptionStatus
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    canceled_at: Optional[datetime]
    trial_start: Optional[datetime]
    trial_end: Optional[datetime]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionUpdate(BaseModel):
    cancel_at_period_end: Optional[bool] = None


class StripeCheckoutRequest(BaseModel):
    plan_id: UUID
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class StripeCheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


class StripePortalRequest(BaseModel):
    return_url: Optional[str] = None


class StripePortalResponse(BaseModel):
    portal_url: str


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    scopes: List[ApiKeyScope] = []
    expires_at: Optional[datetime] = None


class ApiKeyResponse(BaseModel):
    id: UUID
    user_id: UUID
    tenant_id: UUID
    name: str
    key_prefix: str
    scopes: List[ApiKeyScope]
    is_active: bool
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApiKeyCreateResponse(BaseModel):
    api_key: ApiKeyResponse
    plain_key: str


class ApiUsageLogResponse(BaseModel):
    id: UUID
    api_key_id: UUID
    user_id: UUID
    tenant_id: UUID
    endpoint: str
    method: str
    status_code: Optional[int]
    request_size: Optional[int]
    response_size: Optional[int]
    latency_ms: Optional[int]
    ip_address: Optional[str]
    user_agent: Optional[str]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ContactMessageCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=10000)


class ContactMessageResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    tenant_id: Optional[UUID]
    name: str
    email: str
    subject: str
    message: str
    status: ContactStatus
    admin_notes: Optional[str]
    resolved_at: Optional[datetime]
    resolved_by: Optional[UUID]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContactMessageUpdate(BaseModel):
    status: Optional[ContactStatus] = None
    admin_notes: Optional[str] = None


class AdminStatsResponse(BaseModel):
    total_users: int
    total_tenants: int
    total_subscriptions: int
    active_subscriptions: int
    total_api_keys: int
    active_api_keys: int
    total_api_calls_today: int
    total_api_calls_month: int
    revenue_cents: int
    contact_messages: int
    pending_contact_messages: int


class AdminUserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    page_size: int


class AdminTenantListResponse(BaseModel):
    tenants: List[TenantResponse]
    total: int
    page: int
    page_size: int


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
    search_type: str = "hybrid"


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
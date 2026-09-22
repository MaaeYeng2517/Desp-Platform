"""Pydantic schemas for API requests and responses."""
import enum
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from backend.app.models.api_key import ApiKeyScope
from backend.app.models.billing import SubscriptionStatus
from backend.app.models.contact import ContactStatus
from backend.app.models.user import UserRole


class TenantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    settings: Dict[str, Any] = Field(default_factory=dict)


class TenantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: Optional[str]
    settings: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    tenant_id: Optional[UUID] = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    email: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    csrf_token: str
    user: UserResponse


class MembershipPlanCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    stripe_price_id: Optional[str] = None
    stripe_product_id: Optional[str] = None
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    price_cents: int = Field(0, ge=0)
    currency: str = Field("thb", min_length=3, max_length=3)
    interval: str = Field("month", pattern="^(month|year)$")
    api_calls_per_month: int = Field(1000, ge=0)
    features: List[str] = Field(default_factory=list)
    is_active: bool = True
    sort_order: int = Field(0, ge=0)


class MembershipPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
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


class SubscriptionCreate(BaseModel):
    plan_id: UUID
    stripe_payment_method_id: Optional[str] = None


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    metadata: Dict[str, Any] = Field(alias="data", serialization_alias="metadata")
    created_at: datetime
    updated_at: datetime


class SubscriptionUpdate(BaseModel):
    cancel_at_period_end: Optional[bool] = None


class StripeCheckoutRequest(BaseModel):
    plan_id: UUID
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class StripeCheckoutResponse(BaseModel):
    checkout_url: Optional[str] = None
    session_id: Optional[str] = None
    message: Optional[str] = None


class StripePortalRequest(BaseModel):
    return_url: Optional[str] = None


class StripePortalResponse(BaseModel):
    portal_url: str


class EntitlementResponse(BaseModel):
    plan: str
    status: str
    api_calls_limit: int
    features: List[str]
    current_period_end: Optional[datetime] = None


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    scopes: List[ApiKeyScope] = Field(default_factory=lambda: [ApiKeyScope.READ])
    expires_at: Optional[datetime] = None

    @field_validator("scopes")
    @classmethod
    def unique_scopes(cls, value: List[ApiKeyScope]) -> List[ApiKeyScope]:
        return list(dict.fromkeys(value))


class ApiKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class ApiKeyCreateResponse(BaseModel):
    api_key: ApiKeyResponse
    plain_key: str


class ApiUsageLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class ContactMessageCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=10000)


class ContactMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    settings: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class DocumentCreate(BaseModel):
    kb_id: UUID
    title: str
    source_type: str
    source_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kb_id: UUID
    title: str
    source_type: str
    source_url: Optional[str]
    status: str
    version: str
    is_published: bool
    created_at: datetime


class ChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    content: str
    chunk_index: int
    token_count: Optional[int]
    metadata: Dict[str, Any]


class SearchRequest(BaseModel):
    query: str
    kb_ids: List[UUID]
    metadata_filters: Optional[Dict[str, Any]] = None
    limit: int = Field(10, ge=1, le=100)
    score_threshold: Optional[float] = None
    search_type: str = "hybrid"


class SearchResult(BaseModel):
    chunk_id: UUID
    document_id: UUID
    title: str
    content: str
    score: float
    metadata: Dict[str, Any]
    sources: List[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int
    latency_ms: float


class RAGRequest(BaseModel):
    query: str
    kb_ids: List[UUID]
    metadata_filters: Optional[Dict[str, Any]] = None
    limit: int = Field(5, ge=1, le=20)
    temperature: float = Field(0.7, ge=0, le=2)
    max_tokens: int = Field(1000, ge=1, le=10000)


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
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)


class WorkflowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kb_id: UUID
    name: str
    description: Optional[str]
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    is_active: bool
    version: str


class MetadataSchemaCreate(BaseModel):
    kb_id: UUID
    name: str
    description: Optional[str] = None
    fields: List[Dict[str, Any]]
    taxonomy: Dict[str, Any] = Field(default_factory=dict)


class MetadataSchemaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kb_id: UUID
    name: str
    description: Optional[str]
    fields: List[Dict[str, Any]]
    taxonomy: Dict[str, Any]
    is_active: bool


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

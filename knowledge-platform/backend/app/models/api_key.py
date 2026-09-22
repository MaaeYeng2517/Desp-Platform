"""API Key and Usage Logging models"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Enum as SQLEnum, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base
import enum


class ApiKeyScope(str, enum.Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    SEARCH = "search"
    RAG = "rag"
    DOCUMENTS = "documents"
    WORKFLOWS = "workflows"


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    tenant_id = Column(UUID, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    key_prefix = Column(String(12), nullable=False, index=True)
    key_hash = Column(String, nullable=False)
    key_hmac = Column(String, nullable=False)
    scopes = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="api_keys")
    tenant = relationship("Tenant")
    usage_logs = relationship("ApiUsageLog", back_populates="api_key")

    __table_args__ = (
        Index("ix_api_keys_tenant_user", "tenant_id", "user_id"),
        Index("ix_api_keys_prefix_active", "key_prefix", "is_active"),
    )


class ApiUsageLog(Base):
    __tablename__ = "api_usage_logs"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    api_key_id = Column(UUID, ForeignKey("api_keys.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    tenant_id = Column(UUID, ForeignKey("tenants.id"), nullable=False)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer)
    request_size = Column(Integer)
    response_size = Column(Integer)
    latency_ms = Column(Integer)
    ip_address = Column(String)
    user_agent = Column(String)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    api_key = relationship("ApiKey", back_populates="usage_logs")
    user = relationship("User", back_populates="api_usage_logs")
    tenant = relationship("Tenant")

    __table_args__ = (
        Index("ix_api_usage_logs_tenant_created", "tenant_id", "created_at"),
        Index("ix_api_usage_logs_user_created", "user_id", "created_at"),
        Index("ix_api_usage_logs_key_created", "api_key_id", "created_at"),
    )
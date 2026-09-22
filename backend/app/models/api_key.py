"""API key and usage logging models."""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database import Base


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
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(UUID, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    key_prefix = Column(String(16), nullable=False, index=True)
    key_hash = Column(String(64), nullable=False, unique=True)
    scopes = Column(JSON, default=list, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)
    revoked_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="api_keys")
    tenant = relationship("Tenant", back_populates="api_keys")
    usage_logs = relationship("ApiUsageLog", back_populates="api_key")

    __table_args__ = (
        Index("ix_api_keys_tenant_user", "tenant_id", "user_id"),
        Index("ix_api_keys_prefix_active", "key_prefix", "is_active"),
    )


class ApiUsageLog(Base):
    __tablename__ = "api_usage_logs"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    api_key_id = Column(UUID, ForeignKey("api_keys.id"), nullable=False, index=True)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(UUID, ForeignKey("tenants.id"), nullable=False, index=True)
    endpoint = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer)
    request_size = Column(Integer)
    response_size = Column(Integer)
    latency_ms = Column(Integer)
    ip_address = Column(String(45))
    user_agent = Column(String(1000))
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    api_key = relationship("ApiKey", back_populates="usage_logs")
    user = relationship("User", back_populates="api_usage_logs")
    tenant = relationship("Tenant")

    __table_args__ = (
        Index("ix_api_usage_logs_tenant_created", "tenant_id", "created_at"),
        Index("ix_api_usage_logs_user_created", "user_id", "created_at"),
        Index("ix_api_usage_logs_key_created", "api_key_id", "created_at"),
    )

"""User model with RBAC"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base
import enum


class UserRole(str, enum.Enum):
    GUEST = "guest"
    MEMBER = "member"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID, ForeignKey("tenants.id"), nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="users")
    knowledge_bases = relationship("KnowledgeBase", back_populates="owner")
    subscriptions = relationship("Subscription", back_populates="user")
    api_keys = relationship("ApiKey", back_populates="user")
    api_usage_logs = relationship("ApiUsageLog", back_populates="user")
    contact_messages = relationship("ContactMessage", back_populates="user")
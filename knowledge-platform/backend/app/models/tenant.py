"""Tenant model for multi-tenant support."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(String(1000))
    settings = Column(JSON, default=dict, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="tenant")
    subscriptions = relationship("Subscription", back_populates="tenant")
    membership_plans = relationship("MembershipPlan", back_populates="tenant")
    api_keys = relationship("ApiKey", back_populates="tenant")
    contact_messages = relationship("ContactMessage", back_populates="tenant")

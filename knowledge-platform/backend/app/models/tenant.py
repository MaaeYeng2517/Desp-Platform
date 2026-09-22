"""Tenant model for multi-tenant support"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String, nullable=False, unique=True, index=True)
    description = Column(String)
    settings = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", back_populates="tenant")
    subscriptions = relationship("Subscription", back_populates="tenant")
    membership_plans = relationship("MembershipPlan", back_populates="tenant")
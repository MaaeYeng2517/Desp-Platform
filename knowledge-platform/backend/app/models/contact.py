"""Contact Message model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base
import enum


class ContactStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    SPAM = "spam"


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    tenant_id = Column(UUID, ForeignKey("tenants.id"))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(SQLEnum(ContactStatus), default=ContactStatus.NEW, nullable=False)
    admin_notes = Column(Text)
    resolved_at = Column(DateTime)
    resolved_by = Column(UUID, ForeignKey("users.id"))
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="contact_messages", foreign_keys=[user_id])
    tenant = relationship("Tenant")
    resolver = relationship("User", foreign_keys=[resolved_by])

    __table_args__ = (
        Index("ix_contact_messages_status_created", "status", "created_at"),
        Index("ix_contact_messages_tenant_status", "tenant_id", "status"),
    )
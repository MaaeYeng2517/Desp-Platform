"""Contact message model."""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database import Base


class ContactStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    SPAM = "spam"


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=True, index=True)
    tenant_id = Column(UUID, ForeignKey("tenants.id"), nullable=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(320), nullable=False, index=True)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(SQLEnum(ContactStatus), default=ContactStatus.NEW, nullable=False, index=True)
    admin_notes = Column(Text)
    resolved_at = Column(DateTime)
    resolved_by = Column(UUID, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(45))
    user_agent = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="contact_messages", foreign_keys=[user_id])
    tenant = relationship("Tenant", back_populates="contact_messages")
    resolver = relationship("User", foreign_keys=[resolved_by])

    __table_args__ = (
        Index("ix_contact_messages_status_created", "status", "created_at"),
        Index("ix_contact_messages_tenant_status", "tenant_id", "status"),
    )

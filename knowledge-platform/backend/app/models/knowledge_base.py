"""Knowledge Base model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID, ForeignKey("tenants.id"), nullable=False)
    owner_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    slug = Column(String, nullable=False)
    settings = Column(JSON, default={})
    is_published = Column(Boolean, default=False)
    status = Column(String, default="draft")  # draft, processing, published, archived
    version = Column(String, default="1.0")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="knowledge_bases")
    owner = relationship("User", back_populates="knowledge_bases")
    documents = relationship("Document", back_populates="knowledge_base")
    metadata_schemas = relationship("MetadataSchema", back_populates="knowledge_base")
    workflows = relationship("Workflow", back_populates="knowledge_base")
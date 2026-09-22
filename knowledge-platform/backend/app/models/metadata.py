"""Metadata Schema model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base


class MetadataSchema(Base):
    __tablename__ = "metadata_schemas"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    kb_id = Column(UUID, ForeignKey("knowledge_bases.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    fields = Column(JSON, nullable=False)  # Field definitions
    taxonomy = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    knowledge_base = relationship("KnowledgeBase", back_populates="metadata_schemas")
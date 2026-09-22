"""Workflow model for visual pipeline builder"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base


class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    kb_id = Column(UUID, ForeignKey("knowledge_bases.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    nodes = Column(JSON, default=[])  # Node definitions
    edges = Column(JSON, default=[])  # Edge connections
    is_active = Column(Boolean, default=True)
    version = Column(String, default="1.0")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    knowledge_base = relationship("KnowledgeBase", back_populates="workflows")
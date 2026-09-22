"""Source connector model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base


class Source(Base):
    __tablename__ = "sources"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    kb_id = Column(UUID, ForeignKey("knowledge_bases.id"), nullable=False)
    name = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    config = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    sync_status = Column(String, default="idle")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
"""Document model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    kb_id = Column(UUID, ForeignKey("knowledge_bases.id"), nullable=False)
    source_id = Column(UUID, ForeignKey("sources.id"))
    title = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # pdf, web, db, api, file, youtube
    source_url = Column(Text)
    file_path = Column(Text)
    file_size = Column(Integer)
    mime_type = Column(String)
    checksum = Column(String)
    content = Column(Text)
    metadata = Column(JSON, default={})
    status = Column(String, default="pending")  # pending, processing, processed, failed
    version = Column(String, default="1.0")
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document")
    entities = relationship("Entity", back_populates="document")
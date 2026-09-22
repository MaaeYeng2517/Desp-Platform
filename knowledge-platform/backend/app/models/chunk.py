"""Chunk model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base


class Chunk(Base):
    __tablename__ = "chunks"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID, ForeignKey("documents.id"), nullable=False)
    kb_id = Column(UUID, ForeignKey("knowledge_bases.id"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_size = Column(Integer)
    token_count = Column(Integer)
    metadata = Column(JSON, default={})
    embedding = Column(JSON)  # Store as JSON, actual vector in Qdrant
    qdrant_point_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="chunks")
    entities = relationship("Entity", back_populates="chunk")
"""Entity and Relationship models for Knowledge Graph"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base


class Entity(Base):
    __tablename__ = "entities"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID, ForeignKey("documents.id"), nullable=False)
    chunk_id = Column(UUID, ForeignKey("chunks.id"))
    kb_id = Column(UUID, ForeignKey("knowledge_bases.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String)  # Person, Organization, Concept, etc.
    description = Column(Text)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="entities")
    chunk = relationship("Chunk", back_populates="entities")
    relationships = relationship("Relationship", foreign_keys="Relationship.subject_id", back_populates="subject")


class Relationship(Base):
    __tablename__ = "relationships"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    kb_id = Column(UUID, ForeignKey("knowledge_bases.id"), nullable=False)
    subject_id = Column(UUID, ForeignKey("entities.id"), nullable=False)
    object_id = Column(UUID, ForeignKey("entities.id"), nullable=False)
    predicate = Column(String, nullable=False)  # teaches, uses, studies, etc.
    weight = Column(Float, default=1.0)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subject = relationship("Entity", foreign_keys=[subject_id], back_populates="relationships")
    object = relationship("Entity", foreign_keys=[object_id])
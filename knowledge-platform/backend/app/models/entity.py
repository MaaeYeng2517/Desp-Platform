"""Entity and Relationship models for Knowledge Graph."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, JSON, String, Text
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
    type = Column(String)
    description = Column(Text)
    data = Column("metadata", JSON, default=dict)
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
    predicate = Column(String, nullable=False)
    weight = Column(Float, default=1.0)
    data = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    subject = relationship("Entity", foreign_keys=[subject_id], back_populates="relationships")
    object = relationship("Entity", foreign_keys=[object_id])

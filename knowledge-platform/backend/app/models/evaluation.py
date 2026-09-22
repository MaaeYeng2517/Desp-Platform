"""Evaluation dataset and metrics models"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base


class EvaluationDataset(Base):
    __tablename__ = "evaluation_datasets"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    kb_id = Column(UUID, ForeignKey("knowledge_bases.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    questions = Column(JSON, default=[])  # List of {question, expected_source, expected_answer}
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    kb_id = Column(UUID, ForeignKey("knowledge_bases.id"), nullable=False)
    dataset_id = Column(UUID, ForeignKey("evaluation_datasets.id"))
    name = Column(String)
    metrics = Column(JSON, default={})
    overall_score = Column(Float)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
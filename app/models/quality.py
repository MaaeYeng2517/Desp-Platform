from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.core.database import Base


class QualityRule(Base):
    __tablename__ = "quality_rules"
    __table_args__ = {"schema": "core"}

    id = PG_UUID(as_uuid=True, primary_key=True, default=uuid4)
    dataset_id = Column(PG_UUID(as_uuid=True), ForeignKey("core.datasets.id"), nullable=False)
    name = Column(String(255), nullable=False)
    rule_type = Column(String(50), nullable=False)
    column_name = Column(String(255), nullable=False)
    rule_config = Column(JSON, nullable=False)
    is_active = Column(String(5), default="true")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class QualityResult(Base):
    __tablename__ = "quality_results"
    __table_args__ = {"schema": "core"}

    id = PG_UUID(as_uuid=True, primary_key=True, default=uuid4)
    dataset_id = Column(PG_UUID(as_uuid=True), ForeignKey("core.datasets.id"), nullable=False)
    rule_id = Column(PG_UUID(as_uuid=True), ForeignKey("core.quality_rules.id"), nullable=True)
    rule_name = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False)
    passed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

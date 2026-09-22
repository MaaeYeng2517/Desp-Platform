from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class DatasetMetadata(Base):
    __tablename__ = "metadata"
    __table_args__ = {"schema": "core"}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    dataset_id = Column(PG_UUID(as_uuid=True), ForeignKey("core.datasets.id"), nullable=False)
    schema_definition = Column(JSON, nullable=False)
    column_count = Column(Integer, nullable=False)
    file_format = Column(String(50), default="csv")
    delimiter = Column(String(10), default=",")
    has_header = Column(String(5), default="true")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    dataset = relationship("Dataset", back_populates="metadata_records")

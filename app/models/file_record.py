from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class FileRecord(Base):
    __tablename__ = "files"
    __table_args__ = {"schema": "core"}

    id = PG_UUID(as_uuid=True, primary_key=True, default=uuid4)
    dataset_id = Column(PG_UUID(as_uuid=True), ForeignKey("core.datasets.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(500), nullable=False)
    bucket = Column(String(100), nullable=False)
    object_name = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    row_count = Column(Integer, nullable=True)
    column_names = Column(JSON, nullable=True)
    checksum = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(50), nullable=False, default="uploaded")

    dataset = relationship("Dataset", back_populates="files")

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Text, MetaData
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(table_name)s_%(column_names)s",
        "uq": "uq_%(table_name)s_%(column_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_names)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class Dataset(Base):
    __tablename__ = "datasets"
    __table_args__ = {"schema": "core"}

    id = PG_UUID(as_uuid=True, primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    source_type = Column(String(50), nullable=False)
    source_path = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="draft")
    created_by = Column(String(255), nullable=False, default="system")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    files = relationship("FileRecord", back_populates="dataset", cascade="all, delete-orphan")
    metadata_records = relationship("DatasetMetadata", back_populates="dataset", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="dataset", cascade="all, delete-orphan")

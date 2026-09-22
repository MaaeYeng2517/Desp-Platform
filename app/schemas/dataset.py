from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DatasetStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class DatasetBase(BaseModel):
    name: str = Field(..., max_length=255, description="Unique dataset name")
    description: Optional[str] = Field(None, max_length=1000, description="Dataset description")
    source_type: str = Field(..., max_length=50, description="Source type e.g. csv, database, api")
    source_path: Optional[str] = Field(None, max_length=500, description="Source file path or connection string")
    status: DatasetStatus = Field(default=DatasetStatus.DRAFT)
    created_by: str = Field(default="system", max_length=255)


class DatasetCreate(DatasetBase):
    pass


class DatasetUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    source_type: Optional[str] = Field(None, max_length=50)
    source_path: Optional[str] = Field(None, max_length=500)
    status: Optional[DatasetStatus] = None
    created_by: Optional[str] = Field(None, max_length=255)


class DatasetRead(DatasetBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

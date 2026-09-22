from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class MetadataBase(BaseModel):
    file_format: str = Field(default="csv", max_length=50)
    delimiter: str = Field(default=",", max_length=10)
    has_header: bool = True


class SchemaColumn(BaseModel):
    name: str
    type: str
    nullable: bool = True


class DatasetMetadataBase(MetadataBase):
    schema_definition: List[SchemaColumn]
    column_count: int


class DatasetMetadataCreate(DatasetMetadataBase):
    dataset_id: UUID


class DatasetMetadataRead(DatasetMetadataBase):
    id: UUID
    dataset_id: UUID
    schema_definition: List[Dict[str, Any]]
    column_count: int
    updated_at: datetime

    class Config:
        from_attributes = True


class MetadataSummary(BaseModel):
    dataset_id: UUID
    dataset_name: str
    file_format: str
    columns: List[SchemaColumn]
    row_count: Optional[int] = None
    file_size: Optional[int] = None

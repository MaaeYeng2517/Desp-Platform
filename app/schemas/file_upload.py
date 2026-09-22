from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FileStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class FileUploadResponse(BaseModel):
    dataset_id: UUID
    filename: str
    file_path: str
    bucket: str
    object_name: str
    file_size: int
    content_type: str
    row_count: Optional[int] = None
    column_names: Optional[List[str]] = None
    checksum: Optional[str] = None
    status: str = "uploaded"
    message: str = "File uploaded successfully"


class FileRead(BaseModel):
    id: UUID
    dataset_id: UUID
    filename: str
    file_path: str
    bucket: str
    object_name: str
    file_size: int
    content_type: str
    row_count: Optional[int] = None
    column_names: Optional[List[str]] = None
    checksum: Optional[str] = None
    uploaded_at: datetime
    status: str

    class Config:
        from_attributes = True

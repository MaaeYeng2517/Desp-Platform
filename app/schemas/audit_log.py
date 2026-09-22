from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class AuditAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    VALIDATE = "validate"
    CLEAN = "clean"
    TRANSFORM = "transform"
    QUALITY_CHECK = "quality_check"
    PIPELINE_RUN = "pipeline_run"


class AuditStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


class AuditLogBase(BaseModel):
    action: AuditAction
    resource_type: str = Field(..., max_length=100)
    resource_id: Optional[str] = Field(None, max_length=255)
    user: str = Field(default="system", max_length=255)
    status: AuditStatus
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = Field(None, max_length=50)


class AuditLogCreate(AuditLogBase):
    dataset_id: Optional[UUID] = None


class AuditLogRead(AuditLogBase):
    id: UUID
    dataset_id: Optional[UUID] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditLogFilter(BaseModel):
    action: Optional[AuditAction] = None
    resource_type: Optional[str] = None
    user: Optional[str] = None
    status: Optional[AuditStatus] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

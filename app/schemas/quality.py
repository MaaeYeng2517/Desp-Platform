from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class QualityStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


class QualityRuleBase(BaseModel):
    name: str = Field(..., max_length=255)
    rule_type: str = Field(..., max_length=50, description="not_null, unique, range, regex, custom")
    column_name: str = Field(..., max_length=255)
    rule_config: Dict[str, Any]


class QualityRuleCreate(QualityRuleBase):
    dataset_id: UUID


class QualityRuleRead(QualityRuleBase):
    id: UUID
    dataset_id: UUID
    is_active: str
    created_at: datetime

    class Config:
        from_attributes = True


class QualityCheckRun(BaseModel):
    dataset_id: Optional[UUID] = None
    rule_ids: Optional[List[UUID]] = None


class QualityCheckResult(BaseModel):
    rule_name: str
    rule_type: str
    status: QualityStatus
    passed_count: int
    failed_count: int
    error_message: Optional[str] = None


class QualityCheckSummary(BaseModel):
    dataset_id: UUID
    total_rules: int
    passed_rules: int
    failed_rules: int
    results: List[QualityCheckResult]
    overall_status: QualityStatus
    checked_at: datetime = Field(default_factory=datetime.utcnow)

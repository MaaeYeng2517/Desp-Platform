from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


class ColumnValidation(BaseModel):
    column_name: str
    data_type: str
    nullable: bool
    unique: bool
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    regex_pattern: Optional[str] = None


class ValidationRequest(BaseModel):
    dataset_id: Optional[UUID] = None
    rules: List[Dict[str, Any]] = Field(default_factory=list, description="Custom validation rules")


class ValidationResult(BaseModel):
    status: ValidationStatus
    total_records: int
    passed_records: int
    failed_records: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[Dict[str, Any]] = Field(default_factory=list)


class CleaningRequest(BaseModel):
    dataset_id: Optional[UUID] = None
    remove_duplicates: bool = True
    drop_nulls: List[str] = Field(default_factory=list, description="Columns to drop nulls from")
    fill_nulls: Dict[str, Any] = Field(default_factory=dict, description="Column -> fill value")
    normalize_dates: bool = True
    columns_to_drop: List[str] = Field(default_factory=list)

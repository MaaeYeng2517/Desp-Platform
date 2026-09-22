from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_quality_service
from app.schemas.quality import (
    QualityRuleCreate,
    QualityRuleRead,
    QualityCheckRun,
    QualityCheckSummary,
    QualityCheckResult,
)
from app.services.quality_service import QualityService
from app.models.quality import QualityResult

router = APIRouter(
    prefix="/quality",
    tags=["Quality Check"],
)


@router.post("/rules", response_model=QualityRuleRead, status_code=status.HTTP_201_CREATED)
async def create_quality_rule(
    data: QualityRuleCreate,
    service: QualityService = Depends(get_quality_service),
    current_user: str = "system",
):
    try:
        rule = await service.define_rule(
            dataset_id=data.dataset_id,
            name=data.name,
            rule_type=data.rule_type,
            column_name=data.column_name,
            rule_config=data.rule_config,
            current_user=current_user,
        )
        return rule
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/rules/{dataset_id}", response_model=List[QualityRuleRead])
async def list_quality_rules(
    dataset_id: UUID,
    service: QualityService = Depends(get_quality_service),
):
    return await service.list_rules(dataset_id)


@router.post("/check/{file_id}", response_model=QualityCheckSummary)
async def run_quality_checks(
    file_id: UUID,
    rule_ids: Optional[List[UUID]] = None,
    service: QualityService = Depends(get_quality_service),
    current_user: str = "system",
):
    try:
        return await service.run_checks(file_id, rule_ids=rule_ids, current_user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/check/sales-defaults", response_model=dict)
async def get_default_quality_rules(dataset_name: str = "sales"):
    rules = QualityService.get_default_quality_rules(dataset_name)
    return {"dataset_name": dataset_name, "rules": rules}


@router.get("/results/{dataset_id}", response_model=List)
async def list_quality_results(
    dataset_id: UUID,
    service: QualityService = Depends(get_quality_service),
):
    results = await service.list_results(dataset_id)
    return [
        {
            "id": str(r.id),
            "rule_name": r.rule_name,
            "status": r.status,
            "passed_count": r.passed_count,
            "failed_count": r.failed_count,
            "error_message": r.error_message,
            "executed_at": r.executed_at,
        }
        for r in results
    ]

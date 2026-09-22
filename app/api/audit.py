from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_audit_service
from app.schemas.audit_log import AuditLogRead, AuditLogFilter
from app.services.audit_service import AuditService
from app.models.audit_log import AuditLog

router = APIRouter(
    prefix="/audit",
    tags=["Audit Log"],
)


@router.get("/", response_model=List[AuditLogRead])
async def list_audit_logs(
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    user: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    service: AuditService = Depends(get_audit_service),
):
    filter = AuditLogFilter(
        action=action,
        resource_type=resource_type,
        user=user,
        status=status,
    ) if any([action, resource_type, user, status]) else None

    return await service.query(filter=filter, limit=limit, offset=offset)


@router.get("/{audit_id}", response_model=AuditLogRead)
async def get_audit_log(
    audit_id: UUID,
    service: AuditService = Depends(get_audit_service),
):
    record = await service.get_by_id(audit_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Audit log {audit_id} not found")
    return record


@router.get("/dataset/{dataset_id}", response_model=List[AuditLogRead])
async def get_dataset_audit_logs(
    dataset_id: UUID,
    limit: int = 100,
    service: AuditService = Depends(get_audit_service),
):
    return await service.get_by_dataset(dataset_id, limit=limit)

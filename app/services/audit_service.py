import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc

from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogCreate, AuditLogFilter


class AuditService:
    """Service for recording and querying audit log events."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        action: str,
        resource_type: str,
        status: str,
        resource_id: Optional[str] = None,
        dataset_id: Optional[UUID] = None,
        user: str = "system",
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        record = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            dataset_id=dataset_id,
            user=user,
            status=status,
            details=details,
            ip_address=ip_address,
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def query(
        self,
        filter: Optional[AuditLogFilter] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditLog]:
        stmt = select(AuditLog).order_by(desc(AuditLog.timestamp))

        if filter:
            conditions = []
            if filter.action:
                conditions.append(AuditLog.action == filter.action)
            if filter.resource_type:
                conditions.append(AuditLog.resource_type == filter.resource_type)
            if filter.user:
                conditions.append(AuditLog.user == filter.user)
            if filter.status:
                conditions.append(AuditLog.status == filter.status)
            if filter.start_time:
                conditions.append(AuditLog.timestamp >= filter.start_time)
            if filter.end_time:
                conditions.append(AuditLog.timestamp <= filter.end_time)
            if conditions:
                stmt = stmt.where(or_(*conditions))

        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_dataset(self, dataset_id: UUID, limit: int = 100) -> List[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.dataset_id == dataset_id)
            .order_by(desc(AuditLog.timestamp))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, audit_id: UUID) -> Optional[AuditLog]:
        result = await self.db.execute(select(AuditLog).where(AuditLog.id == audit_id))
        return result.scalar_one_or_none()

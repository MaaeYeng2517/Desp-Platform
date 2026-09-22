from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import Dataset
from app.models.file_record import FileRecord
from app.models.metadata import DatasetMetadata
from app.schemas.dataset import DatasetCreate, DatasetUpdate
from app.services.audit_service import AuditService


class DatasetService:
    """Service for managing datasets (CRUD operations)."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = AuditService(db)

    async def create(
        self,
        data: DatasetCreate,
        current_user: str = "system",
        ip_address: Optional[str] = None,
    ) -> Dataset:
        dataset = Dataset(
            name=data.name,
            description=data.description,
            source_type=data.source_type,
            source_path=data.source_path,
            status=data.status.value,
            created_by=current_user,
        )
        self.db.add(dataset)
        await self.db.commit()
        await self.db.refresh(dataset)

        await self.audit.log(
            action="create",
            resource_type="dataset",
            status="success",
            resource_id=str(dataset.id),
            dataset_id=dataset.id,
            user=current_user,
            details={"name": data.name, "source_type": data.source_type},
            ip_address=ip_address,
        )

        return dataset

    async def get(self, dataset_id: UUID) -> Optional[Dataset]:
        result = await self.db.execute(select(Dataset).where(Dataset.id == dataset_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Dataset]:
        result = await self.db.execute(select(Dataset).where(Dataset.name == name))
        return result.scalar_one_or_none()

    async def list(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dataset]:
        stmt = select(Dataset).order_by(Dataset.created_at.desc())
        if status:
            stmt = stmt.where(Dataset.status == status)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(
        self,
        dataset_id: UUID,
        data: DatasetUpdate,
        current_user: str = "system",
        ip_address: Optional[str] = None,
    ) -> Dataset:
        dataset = await self.get(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")

        update_data = data.model_dump(exclude_unset=True)
        if "status" in update_data and update_data["status"] is not None:
            update_data["status"] = update_data["status"].value

        for field, value in update_data.items():
            setattr(dataset, field, value)

        dataset.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(dataset)

        await self.audit.log(
            action="update",
            resource_type="dataset",
            status="success",
            resource_id=str(dataset_id),
            dataset_id=dataset_id,
            user=current_user,
            details=update_data,
            ip_address=ip_address,
        )

        return dataset

    async def delete(
        self,
        dataset_id: UUID,
        current_user: str = "system",
        ip_address: Optional[str] = None,
    ) -> None:
        dataset = await self.get(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")

        await self.audit.log(
            action="delete",
            resource_type="dataset",
            status="success",
            resource_id=str(dataset_id),
            dataset_id=dataset_id,
            user=current_user,
            details={"name": dataset.name},
            ip_address=ip_address,
        )

        await self.db.delete(dataset)
        await self.db.commit()

    async def get_summary(self, dataset_id: UUID) -> dict:
        dataset = await self.get(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")

        files_result = await self.db.execute(
            select(FileRecord).where(FileRecord.dataset_id == dataset_id)
        )
        files = files_result.scalars().all()

        metadata_result = await self.db.execute(
            select(DatasetMetadata).where(DatasetMetadata.dataset_id == dataset_id)
        )
        metadata = metadata_result.scalar_one_or_none()

        total_size = sum(f.file_size for f in files)
        total_rows = sum(f.row_count for f in files if f.row_count is not None)

        return {
            "id": str(dataset.id),
            "name": dataset.name,
            "description": dataset.description,
            "source_type": dataset.source_type,
            "status": dataset.status,
            "created_by": dataset.created_by,
            "created_at": dataset.created_at.isoformat(),
            "updated_at": dataset.updated_at.isoformat(),
            "file_count": len(files),
            "total_size_bytes": total_size,
            "total_rows": total_rows,
            "schema": metadata.schema_definition if metadata else None,
            "column_count": metadata.column_count if metadata else None,
        }

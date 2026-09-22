import io
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.dataset import Dataset
from app.models.file_record import FileRecord
from app.models.metadata import DatasetMetadata
from app.services.audit_service import AuditService
from app.schemas.metadata import DatasetMetadataCreate, SchemaColumn


class MetadataService:
    """
    Service for managing dataset metadata.

    Extracts schema, column information, and statistics
    from uploaded files and stores them as metadata.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = AuditService(db)

    async def extract_metadata(
        self,
        dataset_id: UUID,
        file_id: Optional[UUID] = None,
        current_user: str = "system",
        ip_address: Optional[str] = None,
    ) -> DatasetMetadata:
        result = await self.db.execute(select(Dataset).where(Dataset.id == dataset_id))
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")

        if file_id:
            file_result = await self.db.execute(select(FileRecord).where(FileRecord.id == file_id))
            file_record = file_result.scalar_one_or_none()
            if not file_record:
                raise ValueError(f"File {file_id} not found")
            schema_def, col_count = self._extract_from_file(file_record)
        else:
            files_result = await self.db.execute(
                select(FileRecord).where(FileRecord.dataset_id == dataset_id)
            )
            files = files_result.scalars().all()
            if not files:
                raise ValueError(f"No files found for dataset {dataset_id}")
            schema_def, col_count = self._extract_from_file(files[0])

        existing_result = await self.db.execute(
            select(DatasetMetadata).where(DatasetMetadata.dataset_id == dataset_id)
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            existing.schema_definition = schema_def
            existing.column_count = col_count
            existing.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(existing)
            metadata = existing
        else:
            metadata = DatasetMetadata(
                dataset_id=dataset_id,
                schema_definition=schema_def,
                column_count=col_count,
            )
            self.db.add(metadata)
            await self.db.commit()
            await self.db.refresh(metadata)

        await self.audit.log(
            action="extract_metadata",
            resource_type="metadata",
            status="success",
            resource_id=str(metadata.id),
            dataset_id=dataset_id,
            user=current_user,
            details={"column_count": col_count, "file_id": str(file_id) if file_id else None},
            ip_address=ip_address,
        )

        return metadata

    def _extract_from_file(self, file_record: FileRecord) -> tuple[List[Dict[str, Any]], int]:
        from minio import Minio

        client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

        response = client.get_object(file_record.bucket, file_record.object_name)
        content = response.read()
        df = pd.read_csv(io.BytesIO(content))

        schema_def = []
        for col_name in df.columns:
            dtype = str(df[col_name].dtype)
            if dtype in ("int64", "float64", "object", "datetime64[ns]"):
                type_map = {
                    "int64": "integer",
                    "float64": "decimal",
                    "object": "string",
                    "datetime64[ns]": "datetime",
                }
                mapped = type_map.get(dtype, "string")
            else:
                mapped = "string"

            nullable = bool(df[col_name].isna().any())
            unique = bool(df[col_name].is_unique)

            schema_def.append({
                "name": col_name,
                "type": mapped,
                "nullable": nullable,
                "unique": unique,
            })

        return schema_def, len(schema_def)

    async def get_metadata(self, dataset_id: UUID) -> Optional[DatasetMetadata]:
        result = await self.db.execute(
            select(DatasetMetadata).where(DatasetMetadata.dataset_id == dataset_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, limit: int = 100, offset: int = 0):
        result = await self.db.execute(
            select(DatasetMetadata).order_by(DatasetMetadata.updated_at.desc()).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def update_metadata(
        self,
        dataset_id: UUID,
        schema_definition: List[Dict[str, Any]],
        current_user: str = "system",
        ip_address: Optional[str] = None,
    ) -> DatasetMetadata:
        result = await self.db.execute(
            select(DatasetMetadata).where(DatasetMetadata.dataset_id == dataset_id)
        )
        metadata = result.scalar_one_or_none()
        if not metadata:
            metadata = DatasetMetadata(
                dataset_id=dataset_id,
                schema_definition=schema_definition,
                column_count=len(schema_definition),
            )
            self.db.add(metadata)
        else:
            metadata.schema_definition = schema_definition
            metadata.column_count = len(schema_definition)
            metadata.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(metadata)

        await self.audit.log(
            action="update_metadata",
            resource_type="metadata",
            status="success",
            resource_id=str(metadata.id),
            dataset_id=dataset_id,
            user=current_user,
            details={"column_count": len(schema_definition)},
            ip_address=ip_address,
        )

        return metadata

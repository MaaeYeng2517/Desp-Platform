import io
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from minio import Minio

from app.core.config import settings
from app.core.minio_client import ensure_bucket
from app.models.file_record import FileRecord
from app.services.audit_service import AuditService


class RawStorageService:
    """
    Service for managing raw storage layer (MinIO bronze bucket).

    Handles uploading/downloading raw files and inspecting them
    for metadata extraction without transformation.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = AuditService(db)

    @property
    def bucket(self) -> str:
        return settings.MINIO_BUCKET_BRONZE

    def _get_client(self) -> Minio:
        return Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

    async def store_raw(
        self,
        dataset_id: UUID,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream",
        current_user: str = "system",
        ip_address: Optional[str] = None,
    ) -> FileRecord:
        client = self._get_client()
        ensure_bucket(client, self.bucket)

        object_name = f"datasets/{str(dataset_id)}/{filename}"

        try:
            client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=io.BytesIO(content),
                length=len(content),
                content_type=content_type,
            )
        except Exception as e:
            await self.audit.log(
                action="raw_store",
                resource_type="raw_file",
                status="failure",
                dataset_id=dataset_id,
                user=current_user,
                details={"error": str(e), "filename": filename},
                ip_address=ip_address,
            )
            raise

        row_count, columns = self._inspect_file(content, content_type)

        record = FileRecord(
            dataset_id=dataset_id,
            filename=filename,
            file_path=f"{self.bucket}/{object_name}",
            bucket=self.bucket,
            object_name=object_name,
            file_size=len(content),
            content_type=content_type,
            row_count=row_count,
            column_names=columns,
            status="stored",
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)

        await self.audit.log(
            action="raw_store",
            resource_type="raw_file",
            status="success",
            resource_id=str(record.id),
            dataset_id=dataset_id,
            user=current_user,
            details={
                "filename": filename,
                "size": len(content),
                "row_count": row_count,
            },
            ip_address=ip_address,
        )

        return record

    def _inspect_file(self, content: bytes, content_type: str) -> Tuple[Optional[int], Optional[List[str]]]:
        if "csv" in content_type or content_type == "text/csv":
            try:
                df = pd.read_csv(io.BytesIO(content))
                return len(df), list(df.columns)
            except Exception:
                return None, None
        return None, None

    async def retrieve_raw(self, file_id: UUID, current_user: str = "system") -> bytes:
        from sqlalchemy import select

        result = await self.db.execute(select(FileRecord).where(FileRecord.id == file_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError(f"File {file_id} not found")

        client = self._get_client()
        response = client.get_object(record.bucket, record.object_name)
        content = response.read()

        await self.audit.log(
            action="raw_retrieve",
            resource_type="raw_file",
            status="success",
            resource_id=str(file_id),
            dataset_id=record.dataset_id,
            user=current_user,
            details={"filename": record.filename},
        )

        return content

    async def list_raw(self, dataset_id: UUID) -> List[FileRecord]:
        from sqlalchemy import select

        result = await self.db.execute(
            select(FileRecord).where(FileRecord.dataset_id == dataset_id)
        )
        return result.scalars().all()

    async def delete_raw(self, file_id: UUID, current_user: str = "system") -> None:
        from sqlalchemy import select

        result = await self.db.execute(select(FileRecord).where(FileRecord.id == file_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError(f"File {file_id} not found")

        client = self._get_client()
        try:
            client.remove_object(record.bucket, record.object_name)
        except Exception:
            pass

        await self.audit.log(
            action="raw_delete",
            resource_type="raw_file",
            status="success",
            resource_id=str(file_id),
            dataset_id=record.dataset_id,
            user=current_user,
        )

        await self.db.delete(record)
        await self.db.commit()

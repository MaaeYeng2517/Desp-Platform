import hashlib
import io
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from minio import Minio

from app.core.config import settings
from app.core.minio_client import ensure_bucket
from app.models.dataset import Dataset
from app.models.file_record import FileRecord
from app.schemas.file_upload import FileUploadResponse
from app.services.audit_service import AuditService
    """Service for handling file uploads to MinIO and tracking metadata."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = AuditService(db)

    def _compute_checksum(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def _inspect_csv(self, content: bytes) -> Tuple[Optional[int], Optional[List[str]]]:
        try:
            df = pd.read_csv(io.BytesIO(content))
            return len(df), list(df.columns)
        except Exception:
            return None, None

    async def upload_file(
        self,
        file: UploadFile,
        dataset_id: UUID,
        bucket: str = None,
        current_user: str = "system",
        ip_address: Optional[str] = None,
    ) -> FileUploadResponse:
        bucket = bucket or settings.MINIO_BUCKET_BRONZE

        result = await self.db.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")

        content = await file.read()
        checksum = self._compute_checksum(content)
        row_count, column_names = self._inspect_csv(content)

        object_name = f"datasets/{str(dataset_id)}/{file.filename}"

        minio_client: Minio = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        ensure_bucket(minio_client, bucket)

        try:
            minio_client.put_object(
                bucket=bucket,
                object_name=object_name,
                data=io.BytesIO(content),
                length=len(content),
                content_type=file.content_type or "application/octet-stream",
            )
        except Exception as e:
            await self.audit.log(
                action="upload",
                resource_type="file",
                status="failure",
                resource_id=str(dataset_id),
                dataset_id=dataset_id,
                user=current_user,
                details={"error": str(e), "filename": file.filename},
                ip_address=ip_address,
            )
            raise

        file_record = FileRecord(
            dataset_id=dataset_id,
            filename=file.filename,
            file_path=f"{bucket}/{object_name}",
            bucket=bucket,
            object_name=object_name,
            file_size=len(content),
            content_type=file.content_type or "application/octet-stream",
            row_count=row_count,
            column_names=column_names,
            checksum=checksum,
            status="uploaded",
        )
        self.db.add(file_record)
        await self.db.commit()
        await self.db.refresh(file_record)

        dataset.updated_at = datetime.utcnow()
        await self.db.commit()

        await self.audit.log(
            action="upload",
            resource_type="file",
            status="success",
            resource_id=str(file_record.id),
            dataset_id=dataset_id,
            user=current_user,
            details={
                "filename": file.filename,
                "file_size": len(content),
                "row_count": row_count,
                "checksum": checksum,
            },
            ip_address=ip_address,
        )

        return FileUploadResponse(
            dataset_id=dataset_id,
            filename=file.filename,
            file_path=f"{bucket}/{object_name}",
            bucket=bucket,
            object_name=object_name,
            file_size=len(content),
            content_type=file.content_type or "application/octet-stream",
            row_count=row_count,
            column_names=column_names,
            checksum=checksum,
        )

    async def download_file(
        self,
        file_id: UUID,
        current_user: str = "system",
        ip_address: Optional[str] = None,
    ) -> Tuple[bytes, str, str]:
        from sqlalchemy import select

        result = await self.db.execute(select(FileRecord).where(FileRecord.id == file_id))
        record = result.scalar_one_or_none()
        if not record:
            raise ValueError(f"File {file_id} not found")

        minio_client: Minio = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

        response = minio_client.get_object(record.bucket, record.object_name)
        content = response.read()

        await self.audit.log(
            action="download",
            resource_type="file",
            status="success",
            resource_id=str(file_id),
            dataset_id=record.dataset_id,
            user=current_user,
            ip_address=ip_address,
        )

        return content, record.filename, record.content_type

    async def list_files(self, dataset_id: UUID) -> List[FileRecord]:
        from sqlalchemy import select

        result = await self.db.execute(
            select(FileRecord).where(FileRecord.dataset_id == dataset_id)
        )
        return result.scalars().all()

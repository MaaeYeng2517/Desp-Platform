import io
import hashlib
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from minio import Minio

from app.core.config import settings
from app.core.minio_client import ensure_bucket
from app.models.file_record import FileRecord
from app.services.audit_service import AuditService
from app.services.validation_service import ValidationService
from app.schemas.validation import CleaningRequest, ValidationResult


class CleaningService:
    """
    Service for data cleaning (Bronze -> Silver layer).

    Handles deduplication, null handling, date normalization,
    and removal of invalid records.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = AuditService(db)

    @property
    def bucket(self) -> str:
        return settings.MINIO_BUCKET_SILVER

    def _get_client(self) -> Minio:
        return Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

    @staticmethod
    def clean_dataframe(
        df: pd.DataFrame,
        request: CleaningRequest,
    ) -> pd.DataFrame:
        cleaned = df.copy()
        original_count = len(cleaned)

        if request.remove_duplicates and "transaction_id" in cleaned.columns:
            cleaned = cleaned.drop_duplicates(subset=["transaction_id"])

        for col in request.drop_nulls:
            if col in cleaned.columns:
                cleaned = cleaned[cleaned[col].notna()]

        for col, fill_value in request.fill_nulls.items():
            if col in cleaned.columns:
                cleaned[col] = cleaned[col].fillna(fill_value)

        if request.normalize_dates:
            for col in cleaned.columns:
                if "date" in col.lower() or "time" in col.lower():
                    try:
                        cleaned[col] = pd.to_datetime(cleaned[col])
                    except (ValueError, TypeError):
                        pass

        for col in request.columns_to_drop:
            if col in cleaned.columns:
                cleaned = cleaned.drop(columns=[col])

        return cleaned

    @staticmethod
    def get_default_cleaning_request(dataset_name: str) -> CleaningRequest:
        if dataset_name == "sales":
            return CleaningRequest(
                remove_duplicates=True,
                fill_nulls={},
                normalize_dates=True,
                columns_to_drop=[],
            )
        return CleaningRequest()

    async def clean_file(
        self,
        file_id: UUID,
        cleaning_request: Optional[CleaningRequest] = None,
        current_user: str = "system",
        ip_address: Optional[str] = None,
    ) -> Tuple[FileRecord, ValidationResult]:
        result = await self.db.execute(select(FileRecord).where(FileRecord.id == file_id))
        source_record = result.scalar_one_or_none()
        if not source_record:
            raise ValueError(f"File {file_id} not found")

        client = self._get_client()
        ensure_bucket(client, self.bucket)

        response = client.get_object(source_record.bucket, source_record.object_name)
        content = response.read()

        df = pd.read_csv(io.BytesIO(content))
        cleaned_df = self.clean_dataframe(df, cleaning_request or self.get_default_cleaning_request("sales"))

        if "quantity" in cleaned_df.columns:
            cleaned_df = cleaned_df[cleaned_df["quantity"] > 0]
        if "unit_price" in cleaned_df.columns:
            cleaned_df = cleaned_df[cleaned_df["unit_price"] >= 0]

        if "transaction_id" in cleaned_df.columns and "quantity" in cleaned_df.columns and "unit_price" in cleaned_df.columns:
            cleaned_df["total_amount"] = cleaned_df["quantity"] * cleaned_df["unit_price"]

        output_buffer = io.StringIO()
        cleaned_df.to_csv(output_buffer, index=False)
        cleaned_content = output_buffer.getvalue().encode("utf-8")

        checksum = hashlib.sha256(cleaned_content).hexdigest()
        object_name = f"datasets/{str(source_record.dataset_id)}/{source_record.filename.replace('.csv', '_clean.csv')}"

        client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=io.BytesIO(cleaned_content),
            length=len(cleaned_content),
            content_type="text/csv",
        )

        cleaned_record = FileRecord(
            dataset_id=source_record.dataset_id,
            filename=f"clean_{source_record.filename}",
            file_path=f"{self.bucket}/{object_name}",
            bucket=self.bucket,
            object_name=object_name,
            file_size=len(cleaned_content),
            content_type="text/csv",
            row_count=len(cleaned_df),
            column_names=list(cleaned_df.columns),
            checksum=checksum,
            status="cleaned",
        )
        self.db.add(cleaned_record)
        await self.db.commit()
        await self.db.refresh(cleaned_record)

        validation_result = ValidationService.validate_dataframe(
            cleaned_df,
            required_columns=["transaction_id"] if "transaction_id" in cleaned_df.columns else [],
            column_validations=None,
            custom_rules=[
                {"type": "positive", "column": "quantity"},
                {"type": "positive", "column": "unit_price"},
            ],
        )

        await self.audit.log(
            action="clean",
            resource_type="file",
            status="success" if validation_result.status.value in ["passed", "warning"] else "failure",
            resource_id=str(cleaned_record.id),
            dataset_id=source_record.dataset_id,
            user=current_user,
            details={
                "original_rows": len(df),
                "cleaned_rows": len(cleaned_df),
                "validation_status": validation_result.status.value,
                "new_checksum": checksum,
            },
            ip_address=ip_address,
        )

        return cleaned_record, validation_result

    async def list_cleaned(self, dataset_id: UUID) -> List[FileRecord]:
        result = await self.db.execute(
            select(FileRecord)
            .where(FileRecord.dataset_id == dataset_id)
            .where(FileRecord.bucket == self.bucket)
        )
        return result.scalars().all()

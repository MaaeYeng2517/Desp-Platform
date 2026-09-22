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
from app.models.quality import QualityResult, QualityRule
from app.services.audit_service import AuditService
from app.services.validation_service import ValidationService
from app.schemas.validation import ValidationResult, ValidationStatus


class TransformationService:
    """
    Service for data transformation (Silver -> Gold layer).

    Handles business-level aggregations and transformations
    stored in the MinIO gold bucket.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = AuditService(db)

    @property
    def bucket(self) -> str:
        return settings.MINIO_BUCKET_GOLD

    def _get_client(self) -> Minio:
        return Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

    @staticmethod
    def aggregate_sales(df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate sales data by transaction date to produce gold layer."""
        if df.empty:
            return pd.DataFrame(columns=["transaction_date", "transaction_count", "units_sold", "revenue"])

        gold_df = (
            df.groupby("transaction_date")
            .agg(
                transaction_count=("transaction_id", "count"),
                units_sold=("quantity", "sum"),
                revenue=("total_amount", "sum"),
            )
            .reset_index()
            .sort_values("transaction_date")
        )

        gold_df["transaction_date"] = gold_df["transaction_date"].astype(str)
        return gold_df

    async def transform_file(
        self,
        file_id: UUID,
        aggregation_type: str = "daily_sales",
        current_user: str = "system",
        ip_address: Optional[str] = None,
    ) -> FileRecord:
        result = await self.db.execute(select(FileRecord).where(FileRecord.id == file_id))
        source_record = result.scalar_one_or_none()
        if not source_record:
            raise ValueError(f"File {file_id} not found")

        client = self._get_client()
        ensure_bucket(client, self.bucket)

        response = client.get_object(source_record.bucket, source_record.object_name)
        content = response.read()

        df = pd.read_csv(io.BytesIO(content))

        if aggregation_type == "daily_sales":
            transformed_df = self.aggregate_sales(df)
        elif aggregation_type == "customer_summary":
            transformed_df = self._aggregate_by_customer(df)
        elif aggregation_type == "product_summary":
            transformed_df = self._aggregate_by_product(df)
        else:
            raise ValueError(f"Unknown aggregation_type: {aggregation_type}")

        output_buffer = io.StringIO()
        transformed_df.to_csv(output_buffer, index=False)
        transformed_content = output_buffer.getvalue().encode("utf-8")

        checksum = hashlib.sha256(transformed_content).hexdigest()
        safe_type = aggregation_type.replace("/", "_")
        object_name = f"datasets/{str(source_record.dataset_id)}/{safe_type}_{source_record.filename}"

        client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=io.BytesIO(transformed_content),
            length=len(transformed_content),
            content_type="text/csv",
        )

        gold_record = FileRecord(
            dataset_id=source_record.dataset_id,
            filename=f"{safe_type}_{source_record.filename}",
            file_path=f"{self.bucket}/{object_name}",
            bucket=self.bucket,
            object_name=object_name,
            file_size=len(transformed_content),
            content_type="text/csv",
            row_count=len(transformed_df),
            column_names=list(transformed_df.columns),
            checksum=checksum,
            status="transformed",
        )
        self.db.add(gold_record)
        await self.db.commit()
        await self.db.refresh(gold_record)

        await self.audit.log(
            action="transform",
            resource_type="file",
            status="success",
            resource_id=str(gold_record.id),
            dataset_id=source_record.dataset_id,
            user=current_user,
            details={
                "aggregation_type": aggregation_type,
                "input_rows": len(df),
                "output_rows": len(transformed_df),
                "new_checksum": checksum,
            },
            ip_address=ip_address,
        )

        return gold_record

    def _aggregate_by_customer(self, df: pd.DataFrame) -> pd.DataFrame:
        result = (
            df.groupby("customer_id")
            .agg(
                total_transactions=("transaction_id", "count"),
                total_units=("quantity", "sum"),
                total_revenue=("total_amount", "sum"),
            )
            .reset_index()
        )
        return result

    def _aggregate_by_product(self, df: pd.DataFrame) -> pd.DataFrame:
        result = (
            df.groupby("product_id")
            .agg(
                total_transactions=("transaction_id", "count"),
                total_units=("quantity", "sum"),
                total_revenue=("total_amount", "sum"),
            )
            .reset_index()
        )
        return result

    async def list_transformed(self, dataset_id: UUID) -> List[FileRecord]:
        result = await self.db.execute(
            select(FileRecord)
            .where(FileRecord.dataset_id == dataset_id)
            .where(FileRecord.bucket == self.bucket)
        )
        return result.scalars().all()

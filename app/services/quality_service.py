import io
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from minio import Minio

from app.core.config import settings
from app.core.minio_client import ensure_bucket
from app.models.file_record import FileRecord
from app.models.quality import QualityRule, QualityResult
from app.models.dataset import Dataset
from app.services.audit_service import AuditService
from app.schemas.quality import QualityCheckResult, QualityCheckSummary, QualityStatus


class QualityService:
    """
    Service for data quality checks.

    Runs configurable quality rules against dataset files
    and stores results for auditing and reporting.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = AuditService(db)

    def _get_client(self) -> Minio:
        return Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

    async def define_rule(
        self,
        dataset_id: UUID,
        name: str,
        rule_type: str,
        column_name: str,
        rule_config: Dict[str, Any],
        current_user: str = "system",
        ip_address: Optional[str] = None,
    ) -> QualityRule:
        rule = QualityRule(
            dataset_id=dataset_id,
            name=name,
            rule_type=rule_type,
            column_name=column_name,
            rule_config=rule_config,
            is_active="true",
        )
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)

        await self.audit.log(
            action="create",
            resource_type="quality_rule",
            status="success",
            resource_id=str(rule.id),
            dataset_id=dataset_id,
            user=current_user,
            details={"name": name, "rule_type": rule_type, "column_name": column_name},
            ip_address=ip_address,
        )

        return rule

    async def list_rules(self, dataset_id: UUID) -> List[QualityRule]:
        result = await self.db.execute(
            select(QualityRule).where(
                and_(
                    QualityRule.dataset_id == dataset_id,
                    QualityRule.is_active == "true",
                )
            )
        )
        return result.scalars().all()

    async def run_checks(
        self,
        file_id: UUID,
        rule_ids: Optional[List[UUID]] = None,
        current_user: str = "system",
        ip_address: Optional[str] = None,
    ) -> QualityCheckSummary:
        result = await self.db.execute(select(FileRecord).where(FileRecord.id == file_id))
        file_record = result.scalar_one_or_none()
        if not file_record:
            raise ValueError(f"File {file_id} not found")

        if rule_ids:
            rules_result = await self.db.execute(
                select(QualityRule).where(QualityRule.id.in_(rule_ids))
            )
            rules = rules_result.scalars().all()
        else:
            rules_result = await self.db.execute(
                select(QualityRule).where(
                    and_(
                        QualityRule.dataset_id == file_record.dataset_id,
                        QualityRule.is_active == "true",
                    )
                )
            )
            rules = rules_result.scalars().all()

        client = self._get_client()
        response = client.get_object(file_record.bucket, file_record.object_name)
        content = response.read()
        df = pd.read_csv(io.BytesIO(content))

        check_results: List[QualityCheckResult] = []
        passed_count = 0
        failed_count = 0

        for rule in rules:
            result = await self._execute_rule(df, rule, file_record.dataset_id, current_user, ip_address)
            check_results.append(result)
            if result.status == QualityStatus.PASS:
                passed_count += 1
            else:
                failed_count += 1

        overall_status = QualityStatus.PASS if failed_count == 0 else QualityStatus.FAIL

        summary = QualityCheckSummary(
            dataset_id=file_record.dataset_id,
            total_rules=len(rules),
            passed_rules=passed_count,
            failed_rules=failed_count,
            results=check_results,
            overall_status=overall_status,
        )

        await self.audit.log(
            action="quality_check",
            resource_type="file",
            status="success" if overall_status == QualityStatus.PASS else "failure",
            resource_id=str(file_id),
            dataset_id=file_record.dataset_id,
            user=current_user,
            details={
                "rules_total": len(rules),
                "rules_passed": passed_count,
                "rules_failed": failed_count,
            },
            ip_address=ip_address,
        )

        return summary

    async def _execute_rule(
        self,
        df: pd.DataFrame,
        rule: QualityRule,
        dataset_id: UUID,
        current_user: str,
        ip_address: Optional[str],
    ) -> QualityCheckResult:
        col = rule.column_name
        config = rule.rule_config
        passed = 0
        failed = 0
        error_message = None

        try:
            if col not in df.columns:
                return QualityCheckResult(
                    rule_name=rule.name,
                    rule_type=rule.rule_type,
                    status=QualityStatus.FAIL,
                    passed_count=0,
                    failed_count=len(df),
                    error_message=f"Column '{col}' not found in data",
                )

            if rule.rule_type == "not_null":
                null_mask = df[col].isna()
                failed = int(null_mask.sum())
                passed = int(len(df) - failed)

            elif rule.rule_type == "unique":
                dup_mask = df[col].duplicated(keep=False)
                failed = int(dup_mask.sum())
                passed = int(len(df) - failed)

            elif rule.rule_type == "range":
                min_val = config.get("min_value")
                max_val = config.get("max_value")
                if min_val is not None and max_val is not None:
                    bad_mask = (df[col] < min_val) | (df[col] > max_val)
                elif min_val is not None:
                    bad_mask = df[col] < min_val
                elif max_val is not None:
                    bad_mask = df[col] > max_val
                else:
                    bad_mask = pd.Series([False] * len(df))
                failed = int(bad_mask.sum())
                passed = int(len(df) - failed)

            elif rule.rule_type == "regex":
                import re
                pattern = config.get("pattern", "")
                compiled = re.compile(pattern)
                non_matching = ~df[col].dropna().apply(lambda x: bool(compiled.match(str(x))))
                failed = int(non_matching.sum())
                passed = int(len(df.dropna()) - failed)

            elif rule.rule_type == "positive":
                if df[col].dtype in ["int64", "float64"]:
                    bad_mask = df[col] <= 0
                    failed = int(bad_mask.sum())
                    passed = int(len(df) - failed)

            else:
                return QualityCheckResult(
                    rule_name=rule.name,
                    rule_type=rule.rule_type,
                    status=QualityStatus.WARNING,
                    passed_count=0,
                    failed_count=0,
                    error_message=f"Unknown rule type: {rule.rule_type}",
                )

            status = QualityStatus.PASS if failed == 0 else QualityStatus.FAIL

            qr = QualityResult(
                dataset_id=dataset_id,
                rule_id=rule.id,
                rule_name=rule.name,
                status=status.value,
                passed_count=passed,
                failed_count=failed,
                error_message=error_message,
            )
            self.db.add(qr)
            await self.db.commit()

            return QualityCheckResult(
                rule_name=rule.name,
                rule_type=rule.rule_type,
                status=status,
                passed_count=passed,
                failed_count=failed,
                error_message=error_message,
            )

        except Exception as e:
            error_message = str(e)
            return QualityCheckResult(
                rule_name=rule.name,
                rule_type=rule.rule_type,
                status=QualityStatus.FAIL,
                passed_count=0,
                failed_count=len(df),
                error_message=error_message,
            )

    async def list_results(self, dataset_id: UUID) -> List[QualityResult]:
        result = await self.db.execute(
            select(QualityResult).where(QualityResult.dataset_id == dataset_id)
        )
        return result.scalars().all()

    @staticmethod
    def get_default_quality_rules(dataset_name: str) -> List[Dict[str, Any]]:
        if dataset_name == "sales":
            return [
                {
                    "name": "unique_transaction_id",
                    "rule_type": "unique",
                    "column_name": "transaction_id",
                    "rule_config": {},
                },
                {
                    "name": "positive_quantity",
                    "rule_type": "positive",
                    "column_name": "quantity",
                    "rule_config": {},
                },
                {
                    "name": "non_negative_price",
                    "rule_type": "range",
                    "column_name": "unit_price",
                    "rule_config": {"min_value": 0},
                },
                {
                    "name": "not_null_customer",
                    "rule_type": "not_null",
                    "column_name": "customer_id",
                    "rule_config": {},
                },
            ]
        return []

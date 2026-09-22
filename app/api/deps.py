from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.database import get_db
from app.services.dataset_service import DatasetService
from app.services.file_service import FileUploadService
from app.services.raw_storage_service import RawStorageService
from app.services.validation_service import ValidationService
from app.services.cleaning_service import CleaningService
from app.services.transformation_service import TransformationService
from app.services.quality_service import QualityService
from app.services.metadata_service import MetadataService
from app.services.audit_service import AuditService


def get_dataset_service(db: AsyncSession = Depends(get_db)) -> DatasetService:
    return DatasetService(db)


def get_file_service(db: AsyncSession = Depends(get_db)) -> FileUploadService:
    return FileUploadService(db)


def get_raw_storage_service(db: AsyncSession = Depends(get_db)) -> RawStorageService:
    return RawStorageService(db)


def get_validation_service() -> ValidationService:
    return ValidationService()


def get_cleaning_service(db: AsyncSession = Depends(get_db)) -> CleaningService:
    return CleaningService(db)


def get_transformation_service(db: AsyncSession = Depends(get_db)) -> TransformationService:
    return TransformationService(db)


def get_quality_service(db: AsyncSession = Depends(get_db)) -> QualityService:
    return QualityService(db)


def get_metadata_service(db: AsyncSession = Depends(get_db)) -> MetadataService:
    return MetadataService(db)


def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    return AuditService(db)

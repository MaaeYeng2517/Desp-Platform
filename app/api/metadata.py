from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_metadata_service, get_db
from app.schemas.metadata import DatasetMetadataCreate, DatasetMetadataRead, MetadataSummary, SchemaColumn
from app.services.metadata_service import MetadataService
from app.models.dataset import Dataset
from app.models.file_record import FileRecord
from app.models.metadata import DatasetMetadata

router = APIRouter(
    prefix="/metadata",
    tags=["Metadata"],
)


@router.post("/", response_model=DatasetMetadataRead, status_code=status.HTTP_201_CREATED)
async def create_metadata(
    data: DatasetMetadataCreate,
    service: MetadataService = Depends(get_metadata_service),
    current_user: str = "system",
):
    existing = await service.get_metadata(data.dataset_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Metadata for dataset {data.dataset_id} already exists",
        )
    return await service.update_metadata(
        data.dataset_id, data.schema_definition, current_user=current_user
    )


@router.get("/{dataset_id}/record", response_model=Optional[DatasetMetadataRead])
async def get_metadata_record(
    dataset_id: UUID,
    service: MetadataService = Depends(get_metadata_service),
):
    metadata = await service.get_metadata(dataset_id)
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Metadata for dataset {dataset_id} not found")
    return metadata


@router.put("/{dataset_id}/record", response_model=DatasetMetadataRead)
async def update_metadata_record(
    dataset_id: UUID,
    schema_definition: List,
    service: MetadataService = Depends(get_metadata_service),
    current_user: str = "system",
):
    return await service.update_metadata(dataset_id, schema_definition, current_user=current_user)


@router.post("/{dataset_id}/extract", response_model=DatasetMetadataRead)
async def extract_metadata(
    dataset_id: UUID,
    file_id: Optional[UUID] = None,
    service: MetadataService = Depends(get_metadata_service),
    current_user: str = "system",
):
    try:
        return await service.extract_metadata(dataset_id, file_id, current_user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{dataset_id}/summary", response_model=MetadataSummary)
async def get_metadata_summary(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    files_result = await db.execute(
        select(FileRecord).where(FileRecord.dataset_id == dataset_id)
    )
    files = files_result.scalars().all()

    metadata_result = await db.execute(
        select(DatasetMetadata).where(DatasetMetadata.dataset_id == dataset_id)
    )
    metadata = metadata_result.scalar_one_or_none()

    columns: List[SchemaColumn] = []
    if metadata and metadata.schema_definition:
        for col in metadata.schema_definition:
            columns.append(SchemaColumn(**col))

    row_count = files[0].row_count if files and files[0].row_count else None
    file_size = files[0].file_size if files else None

    return MetadataSummary(
        dataset_id=dataset_id,
        dataset_name=dataset.name,
        file_format=metadata.file_format if metadata else "csv",
        columns=columns,
        row_count=row_count,
        file_size=file_size,
    )

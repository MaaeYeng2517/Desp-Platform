from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_dataset_service
from app.schemas.dataset import DatasetCreate, DatasetRead, DatasetUpdate, DatasetStatus
from app.models.dataset import Dataset

router = APIRouter(
    prefix="/datasets",
    tags=["Dataset Management"],
)


@router.post("/", response_model=DatasetRead, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    data: DatasetCreate,
    service: DatasetService := Depends(get_dataset_service),
    current_user: str = "system",
):
    existing = await service.get_by_name(data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Dataset with name '{data.name}' already exists",
        )
    return await service.create(data, current_user=current_user)


@router.get("/", response_model=List[DatasetRead])
async def list_datasets(
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    service: DatasetService = Depends(get_dataset_service),
):
    return await service.list(status=status, limit=limit, offset=offset)


@router.get("/{dataset_id}", response_model=DatasetRead)
async def get_dataset(
    dataset_id: UUID,
    service: DatasetService = Depends(get_dataset_service),
):
    dataset = await service.get(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
    return dataset


@router.put("/{dataset_id}", response_model=DatasetRead)
async def update_dataset(
    dataset_id: UUID,
    data: DatasetUpdate,
    service: DatasetService = Depends(get_dataset_service),
    current_user: str = "system",
):
    try:
        return await service.update(dataset_id, data, current_user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: UUID,
    service: DatasetService = Depends(get_dataset_service),
    current_user: str = "system",
):
    try:
        await service.delete(dataset_id, current_user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{dataset_id}/summary")
async def dataset_summary(
    dataset_id: UUID,
    service: DatasetService = Depends(get_dataset_service),
):
    try:
        return await service.get_summary(dataset_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

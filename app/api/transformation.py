from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_transformation_service
from app.services.transformation_service import TransformationService

router = APIRouter(
    prefix="/transformation",
    tags=["Transformation"],
)


@router.post("/{file_id}/transform", response_model=dict)
async def transform_file(
    file_id: UUID,
    aggregation_type: str = "daily_sales",
    service: TransformationService = Depends(get_transformation_service),
    current_user: str = "system",
):
    valid_types = ["daily_sales", "customer_summary", "product_summary"]
    if aggregation_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid aggregation_type. Must be one of: {valid_types}",
        )

    try:
        record = await service.transform_file(file_id, aggregation_type, current_user=current_user)
        return {
            "file_id": str(record.id),
            "filename": record.filename,
            "bucket": record.bucket,
            "object_name": record.object_name,
            "row_count": record.row_count,
            "column_names": record.column_names,
            "checksum": record.checksum,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{dataset_id}/list", response_model=List)
async def list_transformed_files(
    dataset_id: UUID,
    service: TransformationService = Depends(get_transformation_service),
):
    files = await service.list_transformed(dataset_id)
    return [
        {
            "id": str(f.id),
            "filename": f.filename,
            "file_path": f.file_path,
            "file_size": f.file_size,
            "row_count": f.row_count,
            "column_names": f.column_names,
            "checksum": f.checksum,
            "uploaded_at": f.uploaded_at,
        }
        for f in files
    ]

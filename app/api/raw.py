from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.api.deps import get_raw_storage_service
from app.schemas.file_upload import FileUploadResponse
from app.services.raw_storage_service import RawStorageService

router = APIRouter(
    prefix="/raw",
    tags=["Raw Storage"],
)


@router.post("/store", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def store_raw_file(
    file: UploadFile = File(...),
    dataset_id: UUID = None,
    content_type_override: Optional[str] = None,
    service: RawStorageService = Depends(get_raw_storage_service),
    current_user: str = "system",
):
    if dataset_id is None:
        raise HTTPException(status_code=400, detail="dataset_id is required")

    content = await file.read()
    ct = content_type_override or file.content_type or "application/octet-stream"

    record = await service.store_raw(
        dataset_id=dataset_id,
        filename=file.filename,
        content=content,
        content_type=ct,
        current_user=current_user,
    )

    return FileUploadResponse(
        dataset_id=dataset_id,
        filename=record.filename,
        file_path=record.file_path,
        bucket=record.bucket,
        object_name=record.object_name,
        file_size=record.file_size,
        content_type=record.content_type,
        row_count=record.row_count,
        column_names=record.column_names,
        checksum=record.checksum,
    )


@router.get("/{dataset_id}", response_model=List)
async def list_raw_files(
    dataset_id: UUID,
    service: RawStorageService = Depends(get_raw_storage_service),
):
    files = await service.list_raw(dataset_id)
    return [
        {
            "id": str(f.id),
            "filename": f.filename,
            "file_path": f.file_path,
            "file_size": f.file_size,
            "content_type": f.content_type,
            "row_count": f.row_count,
            "column_names": f.column_names,
            "uploaded_at": f.uploaded_at,
            "status": f.status,
        }
        for f in files
    ]


@router.get("/{dataset_id}/{file_id}/download")
async def download_raw_file(
    file_id: UUID,
    service: RawStorageService = Depends(get_raw_storage_service),
    current_user: str = "system",
):
    try:
        content = await service.retrieve_raw(file_id, current_user=current_user)
        from fastapi.responses import Response
        return Response(
            content=content,
            media_type="application/octet-stream",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

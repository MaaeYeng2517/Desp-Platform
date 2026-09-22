from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.api.deps import get_file_service, get_raw_storage_service
from app.schemas.file_upload import FileUploadResponse, FileRead
from app.services.file_service import FileUploadService
from app.services.raw_storage_service import RawStorageService
from app.services.validation_service import ValidationService
from app.schemas.validation import ValidationResult

router = APIRouter(
    prefix="/files",
    tags=["File Upload"],
)


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    dataset_id: UUID = None,
    bucket: Optional[str] = None,
    service: FileUploadService = Depends(get_file_service),
    current_user: str = "system",
):
    if dataset_id is None:
        raise HTTPException(status_code=400, detail="dataset_id is required")
    return await service.upload_file(file, dataset_id, bucket=bucket, current_user=current_user)


@router.get("/upload/valid", response_model=ValidationResult)
async def validate_upload(
    file: UploadFile = File(...),
    dataset_name: str = "sales",
):
    content = await file.read()
    required_columns = ["transaction_id", "transaction_date", "customer_id", "product_id", "quantity", "unit_price"] if dataset_name == "sales" else []
    column_validations = ValidationService.get_default_column_validations(dataset_name)
    result = ValidationService.validate_csv_content(
        content,
        required_columns=required_columns,
        column_validations=column_validations,
    )
    return result


@router.post("/upload/multiple", response_model=List[FileUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    dataset_id: UUID = None,
    bucket: Optional[str] = None,
    service: FileUploadService = Depends(get_file_service),
    current_user: str = "system",
):
    if dataset_id is None:
        raise HTTPException(status_code=400, detail="dataset_id is required")
    results = []
    for f in files:
        result = await service.upload_file(f, dataset_id, bucket=bucket, current_user=current_user)
        results.append(result)
    return results


@router.get("/download/{file_id}")
async def download_file(
    file_id: UUID,
    service: FileUploadService = Depends(get_file_service),
    current_user: str = "system",
):
    try:
        content, filename, content_type = await service.download_file(file_id, current_user=current_user)
        from fastapi.responses import Response
        return Response(
            content=content,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/list/{dataset_id}", response_model=List[FileRead])
async def list_files(
    dataset_id: UUID,
    service: FileUploadService = Depends(get_file_service),
):
    return await service.list_files(dataset_id)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: UUID,
    raw_service: RawStorageService = Depends(get_raw_storage_service),
    current_user: str = "system",
):
    try:
        await raw_service.delete_raw(file_id, current_user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

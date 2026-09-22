from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.api.deps import get_cleaning_service
from app.schemas.validation import CleaningRequest, ValidationResult
from app.services.cleaning_service import CleaningService

router = APIRouter(
    prefix="/cleaning",
    tags=["Cleaning"],
)


@router.post("/{file_id}", response_model=dict)
async def clean_file(
    file_id: UUID,
    params: Optional[CleaningRequest] = None,
    service: CleaningService = Depends(get_cleaning_service),
    current_user: str = "system",
):
    cleaning_request = params or CleaningService.get_default_cleaning_request("sales")

    try:
        record, validation = await service.clean_file(file_id, cleaning_request, current_user=current_user)
        return {
            "file_id": str(record.id),
            "filename": record.filename,
            "bucket": record.bucket,
            "object_name": record.object_name,
            "row_count": record.row_count,
            "column_names": record.column_names,
            "checksum": record.checksum,
            "validation": validation.model_dump(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/preview", response_model=dict)
async def preview_cleaning(
    params: CleaningRequest,
    file: UploadFile = File(...),
):
    import io
    import pandas as pd

    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    cleaned_df = CleaningService.clean_dataframe(df, params)

    return {
        "original_rows": len(df),
        "cleaned_rows": len(cleaned_df),
        "original_columns": list(df.columns),
        "cleaned_columns": list(cleaned_df.columns),
        "preview": cleaned_df.head(10).to_dict(orient="records"),
    }

import io
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import settings
from app.models.dataset import Dataset
from app.models.file_record import FileRecord
from app.core.database import SyncEngine
from app.services.audit_service import AuditService

router = APIRouter(
    prefix="/serve",
    tags=["Data Serving"],
)


@router.get("/query")
async def query_data(
    sql: str = Query(..., description="SQL query to execute on the data warehouse"),
    limit: int = 1000,
    db: AsyncSession = Depends(get_db),
):
    if not sql.strip().lower().startswith("select"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only SELECT queries are allowed",
        )

    try:
        result = await db.execute(text(sql))
        rows = result.fetchall()
        columns = result.keys()

        data = [dict(zip(columns, row)) for row in rows[:limit]]
        return {
            "columns": list(columns),
            "rows": data,
            "row_count": len(data),
            "query": sql[:500],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}",
        )


@router.get("/datasets/{dataset_id}/export")
async def export_dataset(
    dataset_id: UUID,
    format: str = Query("csv", regex="^(csv|json)$"),
    bucket: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    files_result = await db.execute(
        select(FileRecord).where(
            FileRecord.dataset_id == dataset_id,
            FileRecord.bucket == (bucket or settings.MINIO_BUCKET_GOLD),
        )
    )
    files = files_result.scalars().all()

    if not files:
        raise HTTPException(
            status_code=404,
            detail=f"No files found in bucket '{bucket or settings.MINIO_BUCKET_GOLD}' for dataset",
        )

    from minio import Minio
    client = Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )

    import pandas as pd

    all_data = []
    for f in files:
        response = client.get_object(f.bucket, f.object_name)
        content = response.read()
        df = pd.read_csv(io.BytesIO(content))
        all_data.append(df)

    combined = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

    if format == "json":
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={
                "dataset_id": str(dataset_id),
                "dataset_name": dataset.name,
                "format": format,
                "row_count": len(combined),
                "columns": list(combined.columns) if not combined.empty else [],
                "data": combined.to_dict(orient="records"),
            },
        )

    import csv as csv_module
    from fastapi.responses import StreamingResponse

    output = io.StringIO()
    combined.to_csv(output, index=False)
    response = io.BytesIO(output.getvalue().encode("utf-8"))

    return StreamingResponse(
        iter([response.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={dataset.name}_export.csv"},
    )


@router.get("/datasets/{dataset_id}/info")
async def get_dataset_info(
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

    return {
        "id": str(dataset.id),
        "name": dataset.name,
        "description": dataset.description,
        "source_type": dataset.source_type,
        "source_path": dataset.source_path,
        "status": dataset.status,
        "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
        "updated_at": dataset.updated_at.isoformat() if dataset.updated_at else None,
        "files": [
            {
                "id": str(f.id),
                "filename": f.filename,
                "bucket": f.bucket,
                "object_name": f.object_name,
                "file_size": f.file_size,
                "content_type": f.content_type,
                "row_count": f.row_count,
                "column_names": f.column_names,
                "checksum": f.checksum,
                "status": f.status,
                "uploaded_at": f.uploaded_at.isoformat() if f.uploaded_at else None,
            }
            for f in files
        ],
    }

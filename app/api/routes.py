from fastapi import APIRouter

from app.api.datasets import router as dataset_router
from app.api.files import router as file_router
from app.api.raw import router as raw_router
from app.api.validation import router as validation_router
from app.api.cleaning import router as cleaning_router
from app.api.transformation import router as transformation_router
from app.api.quality import router as quality_router
from app.api.metadata import router as metadata_router
from app.api.audit import router as audit_router
from app.api.monitoring import router as monitoring_router
from app.api.lineage import router as lineage_router
from app.api.serving import router as serving_router

api_router = APIRouter()

api_router.include_router(dataset_router, prefix="/v1")
api_router.include_router(file_router, prefix="/v1")
api_router.include_router(raw_router, prefix="/v1")
api_router.include_router(validation_router, prefix="/v1")
api_router.include_router(cleaning_router, prefix="/v1")
api_router.include_router(transformation_router, prefix="/v1")
api_router.include_router(quality_router, prefix="/v1")
api_router.include_router(metadata_router, prefix="/v1")
api_router.include_router(audit_router, prefix="/v1")
api_router.include_router(monitoring_router, prefix="/v1")
api_router.include_router(lineage_router, prefix="/v1")
api_router.include_router(serving_router, prefix="/v1")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.minio_client import ensure_all_buckets

from minio import Minio

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Data Core Platform API - A unified API for dataset management, file upload, validation, cleaning, transformation, quality checks, metadata management, and audit logging.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    from app.core.database import init_db
    await init_db()

    client = Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )
    ensure_all_buckets(client)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Data Core Platform"}


@app.get("/")
async def root():
    return {
        "service": "Data Core Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "api_base": "/api",
        "endpoints": {
            "datasets": "/api/v1/datasets",
            "files": "/api/v1/files",
            "raw_storage": "/api/v1/raw",
            "validation": "/api/v1/validation",
            "cleaning": "/api/v1/cleaning",
            "transformation": "/api/v1/transformation",
            "quality": "/api/v1/quality",
            "metadata": "/api/v1/metadata",
            "audit": "/api/v1/audit",
        },
    }

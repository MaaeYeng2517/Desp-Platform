from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.routes import api_router
from app.core.config import settings
from app.core.database import engine, init_db
from app.core.minio_client import ensure_all_buckets, get_minio_client

logger = logging.getLogger(__name__)


async def startup_db():
    from app.core.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def startup_minio():
    minio_client = get_minio_client()
    ensure_all_buckets(minio_client)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await startup_db()
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")
    try:
        await startup_minio()
    except Exception as e:
        logger.warning(f"MinIO bucket initialization skipped: {e}")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Data Core Platform API - A unified API for dataset management, file upload, validation, cleaning, transformation, quality checks, metadata management, audit logging, monitoring, lineage tracking, and data serving.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


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
            "monitoring": "/api/v1/monitor",
            "lineage": "/api/v1/lineage",
            "serving": "/api/v1/serve",
        },
    }

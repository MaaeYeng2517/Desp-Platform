"""Main FastAPI application"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
import logging

from backend.config import APP_NAME, APP_VERSION, ALLOWED_ORIGINS, JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
from backend.database import init_db, get_db

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Knowledge Engineering Platform API"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    logger.info("Database initialized")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


# Include API routers
from backend.app.api import (
    auth, tenants, knowledge_bases, documents, search, rag,
    workflows, metadata, evaluation, governance, connectors
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["Tenants"])
app.include_router(knowledge_bases.router, prefix="/api/v1/knowledge-bases", tags=["Knowledge Bases"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["Workflows"])
app.include_router(metadata.router, prefix="/api/v1/metadata", tags=["Metadata"])
app.include_router(evaluation.router, prefix="/api/v1/evaluation", tags=["Evaluation"])
app.include_router(governance.router, prefix="/api/v1/governance", tags=["Governance"])
app.include_router(connectors.router, prefix="/api/v1/connectors", tags=["Connectors"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
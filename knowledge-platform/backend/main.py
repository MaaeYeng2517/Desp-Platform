"""Main FastAPI application."""
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from backend.app.api import (
    admin,
    api_keys,
    auth,
    billing,
    connectors,
    contact,
    documents,
    evaluation,
    governance,
    knowledge_bases,
    metadata,
    rag,
    search,
    tenants,
    workflows,
)
from backend.app.dependencies import require_platform_user
from backend.app.security import verify_csrf_token
from backend.config import (
    ALLOWED_ORIGINS,
    APP_NAME,
    APP_VERSION,
    CSRF_COOKIE_NAME,
    validate_production_config,
)
from backend.database import async_session_factory, init_db

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Knowledge Engineering Platform API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    unsafe = request.method in {"POST", "PUT", "PATCH", "DELETE"}
    public_paths = (
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
        "/api/v1/auth/logout",
        "/api/v1/auth/csrf-token",
        "/api/v1/auth/verify-csrf",
        "/api/v1/billing/webhook",
        "/api/v1/contact",
    )
    if unsafe and not request.url.path.startswith(public_paths):
        has_api_key = bool(request.headers.get("x-api-key"))
        has_bearer = (request.headers.get("authorization") or "").lower().startswith("bearer ")
        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        header_token = request.headers.get("x-csrf-token")
        if not has_api_key and not has_bearer and not verify_csrf_token(header_token, cookie_token):
            raise HTTPException(status_code=403, detail="CSRF token missing or invalid")
    return await call_next(request)


@app.on_event("startup")
async def startup_event():
    await init_db()
    validate_production_config()
    from backend.app.api.billing import seed_default_plans

    async with async_session_factory() as db:
        from backend.app.models.tenant import Tenant

        tenants = (await db.execute(select(Tenant).where(Tenant.is_active.is_(True)))).scalars().all()
        for tenant in tenants:
            await seed_default_plans(db, tenant.id)
    __import__("logging").getLogger(__name__).info("Database initialized")


@app.get("/")
async def root():
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health")
async def health():
    try:
        async with async_session_factory() as db:
            await db.execute(select(1))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["Billing"])
app.include_router(api_keys.router, prefix="/api/v1/api-keys", tags=["API Keys"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(contact.router, prefix="/api/v1", tags=["Contact"])

app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["Tenants"], dependencies=[Depends(require_platform_user)])
app.include_router(knowledge_bases.router, prefix="/api/v1/knowledge-bases", tags=["Knowledge Bases"], dependencies=[Depends(require_platform_user)])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"], dependencies=[Depends(require_platform_user)])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"], dependencies=[Depends(require_platform_user)])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG"], dependencies=[Depends(require_platform_user)])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["Workflows"], dependencies=[Depends(require_platform_user)])
app.include_router(metadata.router, prefix="/api/v1/metadata", tags=["Metadata"], dependencies=[Depends(require_platform_user)])
app.include_router(evaluation.router, prefix="/api/v1/evaluation", tags=["Evaluation"], dependencies=[Depends(require_platform_user)])
app.include_router(governance.router, prefix="/api/v1/governance", tags=["Governance"], dependencies=[Depends(require_platform_user)])
app.include_router(connectors.router, prefix="/api/v1/connectors", tags=["Connectors"], dependencies=[Depends(require_platform_user)])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

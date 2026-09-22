"""API key management endpoints."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.dependencies import (
    log_api_usage,
    require_active_membership,
    require_api_key,
    require_api_scope,
    require_platform_user,
)
from backend.app.models.api_key import ApiKey, ApiKeyScope, ApiUsageLog
from backend.app.models.user import User
from backend.app.schemas import (
    ApiKeyCreate,
    ApiKeyCreateResponse,
    ApiKeyResponse,
    ApiUsageLogResponse,
)
from backend.app.security import generate_api_key
from backend.database import get_db

router = APIRouter()


@router.post("/", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_active_membership),
):
    if key_data.expires_at and key_data.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="API key expiration must be in the future")
    plain_key, prefix, key_hash = generate_api_key()
    api_key = ApiKey(
        user_id=user.id,
        tenant_id=user.tenant_id,
        name=key_data.name.strip(),
        key_prefix=prefix,
        key_hash=key_hash,
        scopes=[scope.value for scope in key_data.scopes] or [ApiKeyScope.READ.value],
        expires_at=key_data.expires_at,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    return ApiKeyCreateResponse(
        api_key=ApiKeyResponse.model_validate(api_key),
        plain_key=plain_key,
    )


@router.get("/", response_model=list[ApiKeyResponse])
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_user),
):
    result = await db.execute(
        select(ApiKey)
        .where(ApiKey.user_id == user.id)
        .order_by(ApiKey.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{key_id}", response_model=ApiKeyResponse)
async def get_api_key(
    key_id,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_user),
):
    result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.id)
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    return key


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_user),
):
    result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.id)
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    key.is_active = False
    key.revoked_at = datetime.utcnow()
    await db.commit()
    return {"message": "API key revoked"}


@router.get("/{key_id}/usage", response_model=list[ApiUsageLogResponse])
async def get_api_key_usage(
    key_id,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_user),
):
    key_result = await db.execute(
        select(ApiKey.id).where(ApiKey.id == key_id, ApiKey.user_id == user.id)
    )
    if key_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="API key not found")
    result = await db.execute(
        select(ApiUsageLog)
        .where(ApiUsageLog.api_key_id == key_id)
        .order_by(ApiUsageLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


@router.get("/usage/me", response_model=list[ApiUsageLogResponse])
async def get_my_usage(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_user),
):
    result = await db.execute(
        select(ApiUsageLog)
        .where(ApiUsageLog.user_id == user.id)
        .order_by(ApiUsageLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


@router.get("/protected/read")
async def protected_read(
    key: ApiKey = Depends(require_api_scope(ApiKeyScope.READ)),
):
    return {"authenticated": True, "scope": ApiKeyScope.READ.value, "key_prefix": key.key_prefix}

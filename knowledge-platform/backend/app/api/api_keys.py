"""API Key management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from typing import Optional, List
import hmac
import hashlib
import secrets

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from backend.database import get_db
from backend.app.models.user import User
from backend.app.models.api_key import ApiKey, ApiKeyScope, ApiUsageLog
from backend.app.schemas import (
    ApiKeyCreate, ApiKeyResponse, ApiKeyCreateResponse,
    ApiUsageLogResponse
)
from backend.app.api.auth import get_current_user, require_platform_access
from backend.config import API_KEY_HMAC_SECRET

router = APIRouter()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

KEY_PREFIX = "kep_"


def generate_api_key() -> tuple[str, str, str]:
    """Generate API key with prefix, returns (full_key, prefix, hash)"""
    random_part = secrets.token_urlsafe(32)
    full_key = f"{KEY_PREFIX}{random_part}"
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    key_hmac = hmac.new(API_KEY_HMAC_SECRET.encode(), full_key.encode(), hashlib.sha256).hexdigest()
    prefix = full_key[:12]
    return full_key, prefix, key_hash, key_hmac


async def get_api_key_auth(
    api_key: Optional[str] = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
) -> Optional[ApiKey]:
    """Authenticate via API key"""
    if not api_key or not api_key.startswith(KEY_PREFIX):
        return None
    
    prefix = api_key[:12]
    result = await db.execute(
        select(ApiKey).options(selectinload(ApiKey.user), selectinload(ApiKey.tenant))
        .where(ApiKey.key_prefix == prefix, ApiKey.is_active == True)
    )
    key = result.scalar_one_or_none()
    
    if not key:
        return None
    
    expected_hmac = hmac.new(API_KEY_HMAC_SECRET.encode(), api_key.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(key.key_hmac, expected_hmac):
        return None
    
    if key.expires_at and key.expires_at < datetime.utcnow():
        return None
    
    return key


async def require_api_key(
    key: ApiKey = Depends(get_api_key_auth)
) -> ApiKey:
    """Require valid API key"""
    if not key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return key


async def require_api_scope(required_scope: ApiKeyScope):
    """Require specific API key scope"""
    async def _check_scope(key: ApiKey = Depends(require_api_key)):
        if required_scope not in key.scopes and ApiKeyScope.ADMIN not in key.scopes:
            raise HTTPException(status_code=403, detail=f"Scope '{required_scope}' required")
        return key
    return _check_scope


async def log_api_usage(
    db: AsyncSession,
    api_key: ApiKey,
    endpoint: str,
    method: str,
    status_code: int,
    request_size: int = 0,
    response_size: int = 0,
    latency_ms: int = 0,
    ip_address: str = None,
    user_agent: str = None,
    error_message: str = None
):
    """Log API usage"""
    log = ApiUsageLog(
        api_key_id=api_key.id,
        user_id=api_key.user_id,
        tenant_id=api_key.tenant_id,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        request_size=request_size,
        response_size=response_size,
        latency_ms=latency_ms,
        ip_address=ip_address,
        user_agent=user_agent,
        error_message=error_message
    )
    db.add(log)
    
    api_key.last_used_at = datetime.utcnow()
    await db.commit()


from datetime import datetime

@router.post("", response_model=ApiKeyCreateResponse, status_code=201)
async def create_api_key(
    key_data: ApiKeyCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_access)
):
    """Create a new API key"""
    full_key, prefix, key_hash, key_hmac = generate_api_key()
    
    api_key = ApiKey(
        user_id=user.id,
        tenant_id=user.tenant_id,
        name=key_data.name,
        key_prefix=prefix,
        key_hash=key_hash,
        key_hmac=key_hmac,
        scopes=[s.value for s in key_data.scopes],
        expires_at=key_data.expires_at
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    
    return ApiKeyCreateResponse(
        api_key=ApiKeyResponse.model_validate(api_key),
        plain_key=full_key
    )


@router.get("", response_model=List[ApiKeyResponse])
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_access)
):
    """List user's API keys (without plain keys)"""
    result = await db.execute(
        select(ApiKey).where(ApiKey.user_id == user.id).order_by(ApiKey.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{key_id}", response_model=ApiKeyResponse)
async def get_api_key(
    key_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_access)
):
    """Get API key details"""
    result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.id)
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    return key


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_access)
):
    """Revoke an API key"""
    result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.id)
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    key.is_active = False
    await db.commit()
    return {"message": "API key revoked"}


@router.get("/{key_id}/usage", response_model=List[ApiUsageLogResponse])
async def get_api_key_usage(
    key_id: str,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_access)
):
    """Get usage logs for an API key"""
    key_result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.id)
    )
    if not key_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="API key not found")
    
    result = await db.execute(
        select(ApiUsageLog)
        .where(ApiUsageLog.api_key_id == key_id)
        .order_by(ApiUsageLog.created_at.desc())
        .limit(limit).offset(offset)
    )
    return result.scalars().all()


@router.get("/usage/me", response_model=List[ApiUsageLogResponse])
async def get_my_usage(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_access)
):
    """Get current user's API usage"""
    result = await db.execute(
        select(ApiUsageLog)
        .where(ApiUsageLog.user_id == user.id)
        .order_by(ApiUsageLog.created_at.desc())
        .limit(limit).offset(offset)
    )
    return result.scalars().all()
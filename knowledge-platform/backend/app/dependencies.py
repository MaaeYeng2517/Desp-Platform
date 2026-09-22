"""Authentication and entitlement dependencies."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import jwt
from fastapi import Cookie, Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.api_key import ApiKey, ApiKeyScope
from backend.app.models.billing import Subscription, SubscriptionStatus
from backend.app.models.user import User, UserRole
from backend.app.security import (
    ACCESS_TOKEN_COOKIE_NAME,
    decode_token,
    get_bearer_token,
    hash_api_key,
)
from backend.config import ADMIN_EMAILS
from backend.database import get_db

security = HTTPBearer(auto_error=False)


@dataclass
class AccessPrincipal:
    user: User
    api_key: Optional[ApiKey] = None


async def get_current_user(
    request: Request,
    access_token: Optional[str] = Cookie(None, alias=ACCESS_TOKEN_COOKIE_NAME),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = get_bearer_token(request.headers.get("authorization")) or access_token
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = decode_token(token, "access")
        user_id = payload.get("user_id")
        if not user_id:
            raise ValueError("Missing user_id")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    result = await db.execute(
        select(User)
        .options(selectinload(User.tenant))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user or not user.is_active or not user.tenant or not user.tenant.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User or tenant is inactive")
    return user


async def get_current_user_optional(
    request: Request,
    access_token: Optional[str] = Cookie(None, alias=ACCESS_TOKEN_COOKIE_NAME),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    try:
        return await get_current_user(request, access_token, db)
    except HTTPException:
        return None


async def require_role(*allowed_roles: UserRole):
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles and not user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN and not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


async def get_active_subscription(db: AsyncSession, user: User) -> Optional[Subscription]:
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == user.id)
        .order_by(Subscription.created_at.desc())
    )
    subscriptions = result.scalars().all()
    return next((subscription for subscription in subscriptions if subscription.is_active), None)


async def require_active_membership(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    if user.role == UserRole.ADMIN or user.is_superuser:
        return user
    if not await get_active_subscription(db, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active membership required",
        )
    return user


def _authenticate_api_key(api_key_value: Optional[str], db: AsyncSession) -> Optional[ApiKey]:
    if not api_key_value or not api_key_value.startswith("kep_"):
        return None
    prefix = api_key_value[:16]
    result = await db.execute(
        select(ApiKey)
        .options(selectinload(ApiKey.user), selectinload(ApiKey.tenant))
        .where(ApiKey.key_prefix == prefix, ApiKey.is_active.is_(True))
    )
    key = result.scalar_one_or_none()
    if not key:
        return None
    expected = hash_api_key(api_key_value)
    if not hmac_compare(key.key_hash, expected):
        return None
    if key.expires_at and key.expires_at < datetime.utcnow():
        return None
    if not key.user or not key.user.is_active or not key.tenant or not key.tenant.is_active:
        return None
    return key


def hmac_compare(left: str, right: str) -> bool:
    import hmac
    return hmac.compare_digest(left, right)


async def require_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> ApiKey:
    key = _authenticate_api_key(x_api_key, db)
    if not key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
    return key


async def require_api_scope(required_scope: ApiKeyScope):
    async def dependency(key: ApiKey = Depends(require_api_key)) -> ApiKey:
        if required_scope not in key.scopes and ApiKeyScope.ADMIN not in key.scopes:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Scope '{required_scope.value}' required")
        return key

    return dependency


async def require_platform_access(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> AccessPrincipal:
    key = _authenticate_api_key(x_api_key, db)
    if key:
        subscription = await get_active_subscription(db, key.user)
        if key.user.role != UserRole.ADMIN and not subscription:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Active membership required",
            )
        return AccessPrincipal(user=key.user, api_key=key)

    user = await get_current_user(request, db=db)
    if user.role == UserRole.ADMIN or user.is_superuser:
        return AccessPrincipal(user=user)
    subscription = await get_active_subscription(db, user)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active membership required",
        )
    return AccessPrincipal(user=user)


async def require_platform_user(
    principal: AccessPrincipal = Depends(require_platform_access),
) -> User:
    return principal.user


async def sync_admin_role(user: User) -> None:
    email = (user.email or "").lower()
    if email in ADMIN_EMAILS:
        user.role = UserRole.ADMIN
        user.is_superuser = True


def log_api_usage(
    db: AsyncSession,
    key: ApiKey,
    endpoint: str,
    method: str,
    status_code: int,
    request_size: int = 0,
    response_size: int = 0,
    latency_ms: int = 0,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    error_message: Optional[str] = None,
):
    from backend.app.models.api_key import ApiUsageLog

    key.last_used_at = datetime.utcnow()
    db.add(
        ApiUsageLog(
            api_key_id=key.id,
            user_id=key.user_id,
            tenant_id=key.tenant_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            request_size=request_size,
            response_size=response_size,
            latency_ms=latency_ms,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=error_message,
        )
    )

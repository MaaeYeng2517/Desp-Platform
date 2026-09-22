"""Authentication API endpoints."""
import re
import uuid
from datetime import datetime

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.dependencies import get_current_user, sync_admin_role
from backend.app.models.billing import MembershipPlan, Subscription, SubscriptionStatus
from backend.app.models.tenant import Tenant
from backend.app.models.user import User, UserRole
from backend.app.schemas import TokenResponse, UserCreate, UserLogin, UserResponse, UserUpdate
from backend.app.security import (
    ACCESS_TOKEN_COOKIE_NAME,
    CSRF_COOKIE_NAME,
    REFRESH_TOKEN_COOKIE_NAME,
    clear_auth_cookies,
    create_access_token,
    create_csrf_token,
    create_refresh_token,
    decode_token,
    hash_password,
    set_auth_cookies,
    verify_csrf_token,
    verify_password,
)
from backend.config import ADMIN_EMAILS
from backend.database import get_db

router = APIRouter()


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "member"


async def _unique_tenant_for_email(db: AsyncSession, email: str) -> Tenant:
    local_part = email.split("@", 1)[0]
    base_slug = _slugify(local_part)
    for attempt in range(100):
        slug = base_slug if attempt == 0 else f"{base_slug}-{uuid.uuid4().hex[:8]}"
        result = await db.execute(select(Tenant.id).where(Tenant.slug == slug))
        if result.scalar_one_or_none() is None:
            tenant = Tenant(
                name=f"{local_part}'s workspace",
                slug=slug,
                description="Workspace created during membership registration",
                is_active=True,
            )
            db.add(tenant)
            await db.flush()
            return tenant
    raise HTTPException(status_code=503, detail="Unable to create workspace")


async def _seed_plans(db: AsyncSession, tenant: Tenant) -> None:
    from backend.app.api.billing import seed_default_plans

    await seed_default_plans(db, tenant.id)


def _token_pair(user: User) -> tuple[str, str, str]:
    payload = {
        "user_id": str(user.id),
        "tenant_id": str(user.tenant_id),
        "email": user.email,
        "role": user.role.value,
    }
    return create_access_token(payload), create_refresh_token(payload), create_csrf_token()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    email = user_data.email.strip().lower()
    existing = await db.execute(select(User.id).where(User.email == email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    tenant = await _unique_tenant_for_email(db, email)
    role = UserRole.ADMIN if email in ADMIN_EMAILS else UserRole.MEMBER
    user = User(
        tenant_id=tenant.id,
        email=email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name.strip() if user_data.full_name else None,
        is_active=True,
        is_superuser=role == UserRole.ADMIN,
        role=role,
    )
    db.add(user)
    await db.flush()
    await _seed_plans(db, tenant)

    free_plan = await db.execute(
        select(MembershipPlan).where(
            MembershipPlan.tenant_id == tenant.id,
            MembershipPlan.code == "free",
        )
    )
    plan = free_plan.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=500, detail="Free membership plan is unavailable")
    db.add(
        Subscription(
            tenant_id=tenant.id,
            user_id=user.id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            metadata={"source": "registration"},
        )
    )
    await db.commit()
    await db.refresh(user)

    access_token, refresh_token, csrf_token = _token_pair(user)
    set_auth_cookies(response, access_token, refresh_token, csrf_token)
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
        csrf_token=csrf_token,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    email = credentials.email.strip().lower()
    result = await db.execute(
        select(User)
        .options(selectinload(User.tenant))
        .where(User.email == email)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active or not user.tenant or not user.tenant.is_active:
        raise HTTPException(status_code=403, detail="Account or workspace is disabled")

    await sync_admin_role(user)
    await db.commit()
    access_token, refresh_token, csrf_token = _token_pair(user)
    set_auth_cookies(response, access_token, refresh_token, csrf_token)
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
        csrf_token=csrf_token,
    )


@router.post("/logout")
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"message": "Logged out"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    refresh_token_value: str | None = Cookie(None, alias=REFRESH_TOKEN_COOKIE_NAME),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token_value:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    try:
        payload = decode_token(refresh_token_value, "refresh")
        user_id = payload.get("user_id")
        if not user_id:
            raise ValueError("Missing user_id")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    result = await db.execute(
        select(User)
        .options(selectinload(User.tenant))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user or not user.is_active or not user.tenant or not user.tenant.is_active:
        raise HTTPException(status_code=401, detail="User or workspace is inactive")
    await sync_admin_role(user)
    await db.commit()
    access_token, new_refresh_token, csrf_token = _token_pair(user)
    set_auth_cookies(response, access_token, new_refresh_token, csrf_token)
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
        csrf_token=csrf_token,
    )


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    update: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if update.full_name is not None:
        user.full_name = update.full_name.strip() or None
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.get("/csrf-token")
async def csrf_token(
    response: Response,
    current: str | None = Cookie(None, alias=CSRF_COOKIE_NAME),
):
    token = current or create_csrf_token()
    response.set_cookie(
        CSRF_COOKIE_NAME,
        token,
        max_age=60 * 60,
        httponly=False,
        secure=False,
        samesite="lax",
        path="/",
    )
    return {"csrf_token": token}


@router.post("/verify-csrf")
async def verify_csrf(
    request: Request,
    current: str | None = Cookie(None, alias=CSRF_COOKIE_NAME),
):
    header = request.headers.get("X-CSRF-Token")
    if not verify_csrf_token(header, current):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
    return {"valid": True}

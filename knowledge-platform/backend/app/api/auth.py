"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
import secrets
import hmac
import hashlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.config import (
    JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    ADMIN_EMAILS, COOKIE_SECURE, COOKIE_SAMESITE, CSRF_SECRET_KEY,
    DEBUG
)
from backend.database import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.tenant import Tenant
from backend.app.schemas import (
    UserCreate, UserLogin, UserResponse, TokenResponse, UserUpdate, UserRole as SchemaUserRole
)

router = APIRouter()
security = HTTPBearer(auto_error=False)

ACCESS_TOKEN_COOKIE_NAME = "access_token"
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"
CSRF_COOKIE_NAME = "csrf_token"


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=30))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_csrf_token() -> str:
    """Generate CSRF token"""
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, expected: str) -> bool:
    """Verify CSRF token using constant-time comparison"""
    return hmac.compare_digest(token, expected)


def set_auth_cookies(response: Response, access_token: str, refresh_token: str, csrf_token: str):
    """Set authentication cookies"""
    cookie_params = {
        "httponly": True,
        "secure": COOKIE_SECURE,
        "samesite": COOKIE_SAMESITE,
        "path": "/",
    }
    response.set_cookie(ACCESS_TOKEN_COOKIE_NAME, access_token, max_age=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60, **cookie_params)
    response.set_cookie(REFRESH_TOKEN_COOKIE_NAME, refresh_token, max_age=30 * 24 * 60 * 60, **cookie_params)
    response.set_cookie(CSRF_COOKIE_NAME, csrf_token, max_age=30 * 24 * 60 * 60, **cookie_params)


def clear_auth_cookies(response: Response):
    """Clear authentication cookies"""
    cookie_params = {
        "httponly": True,
        "secure": COOKIE_SECURE,
        "samesite": COOKIE_SAMESITE,
        "path": "/",
    }
    response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME, **cookie_params)
    response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME, **cookie_params)
    response.delete_cookie(CSRF_COOKIE_NAME, **cookie_params)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(None, alias=ACCESS_TOKEN_COOKIE_NAME),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user from JWT token (Bearer or HttpOnly cookie)"""
    token = None
    if credentials:
        token = credentials.credentials
    elif access_token:
        token = access_token
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    result = await db.execute(
        select(User).options(selectinload(User.tenant)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(None, alias=ACCESS_TOKEN_COOKIE_NAME),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    try:
        return await get_current_user(request, credentials, access_token, db)
    except HTTPException:
        return None


async def require_role(allowed_roles: list[UserRole]):
    """Dependency to require specific role(s)"""
    async def _require_role(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles and not user.is_superuser:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return _require_role


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if user.role != UserRole.ADMIN and not user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


async def require_platform_access(user: User = Depends(get_current_user)) -> User:
    """Require platform access (member or admin)"""
    if user.role == UserRole.GUEST and not user.is_superuser:
        raise HTTPException(status_code=403, detail="Platform access required")
    return user


def get_or_create_tenant(db: AsyncSession, email: str) -> Tenant:
    """Get or create tenant for user registration"""
    domain = email.split("@")[-1].lower()
    result = await db.execute(select(Tenant).where(Tenant.slug == domain))
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        tenant = Tenant(
            name=domain,
            slug=domain,
            description=f"Auto-created tenant for {domain}",
            is_active=True
        )
        db.add(tenant)
        await db.flush()
    
    return tenant


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Register new user with tenant auto-creation"""
    existing = await db.execute(select(User).where(User.email == user_data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if user_data.tenant_id:
        tenant_result = await db.execute(select(Tenant).where(Tenant.id == user_data.tenant_id))
        tenant = tenant_result.scalar_one_or_none()
        if not tenant:
            raise HTTPException(status_code=400, detail="Invalid tenant")
    else:
        tenant = get_or_create_tenant(db, user_data.email)
    
    is_admin_email = user_data.email.lower() in [e.lower() for e in ADMIN_EMAILS]
    role = UserRole.ADMIN if is_admin_email else UserRole.MEMBER
    
    user = User(
        tenant_id=tenant.id,
        email=user_data.email.lower(),
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        role=role
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    access_token = create_access_token({"user_id": str(user.id), "email": user.email, "role": user.role.value})
    refresh_token = create_refresh_token({"user_id": str(user.id)})
    csrf_token = create_csrf_token()
    set_auth_cookies(response, access_token, refresh_token, csrf_token)
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """User login with email and password"""
    result = await db.execute(
        select(User).options(selectinload(User.tenant)).where(User.email == credentials.email.lower())
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    
    access_token = create_access_token({"user_id": str(user.id), "email": user.email, "role": user.role.value})
    refresh_token = create_refresh_token({"user_id": str(user.id)})
    csrf_token = create_csrf_token()
    set_auth_cookies(response, access_token, refresh_token, csrf_token)
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/logout")
async def logout(response: Response):
    """User logout - clear cookies"""
    clear_auth_cookies(response)
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    refresh_token: Optional[str] = Cookie(None, alias=REFRESH_TOKEN_COOKIE_NAME),
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    result = await db.execute(
        select(User).options(selectinload(User.tenant)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    new_access_token = create_access_token({"user_id": str(user.id), "email": user.email, "role": user.role.value})
    new_refresh_token = create_refresh_token({"user_id": str(user.id)})
    csrf_token = create_csrf_token()
    set_auth_cookies(response, new_access_token, new_refresh_token, csrf_token)
    
    return TokenResponse(
        access_token=new_access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    user_update: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.get("/csrf-token")
async def get_csrf_token(
    request: Request,
    response: Response,
    csrf_token: Optional[str] = Cookie(None, alias=CSRF_COOKIE_NAME)
):
    """Get or generate CSRF token"""
    if not csrf_token:
        csrf_token = create_csrf_token()
        response.set_cookie(CSRF_COOKIE_NAME, csrf_token, max_age=30 * 24 * 60 * 60,
                           httponly=True, secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE, path="/")
    return {"csrf_token": csrf_token}


@router.post("/verify-csrf")
async def verify_csrf(
    request: Request,
    csrf_token: Optional[str] = Cookie(None, alias=CSRF_COOKIE_NAME)
):
    """Verify CSRF token from header"""
    header_token = request.headers.get("X-CSRF-Token")
    if not header_token or not csrf_token:
        raise HTTPException(status_code=403, detail="CSRF token missing")
    if not verify_csrf_token(header_token, csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
    return {"valid": True}
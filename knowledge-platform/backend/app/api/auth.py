"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import jwt

from backend.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
from backend.app.schemas import UserCreate, UserResponse

router = APIRouter()
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/register")
async def register(user: UserCreate):
    """Register new user"""
    return {
        "message": "User registered",
        "user_id": "placeholder",
        "email": user.email
    }


@router.post("/login")
async def login(email: str, password: str):
    """User login"""
    # Placeholder - in production, verify against database
    token = create_access_token({"user_id": "placeholder", "email": email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": "placeholder",
        "email": email
    }


@router.get("/me")
async def get_current_user_info(user_id: str = Depends(get_current_user)):
    """Get current user info"""
    return {
        "user_id": user_id,
        "message": "Current user info"
    }
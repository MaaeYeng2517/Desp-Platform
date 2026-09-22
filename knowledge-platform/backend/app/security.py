"""Security primitives for authentication and API keys."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import Response
from sqlalchemy import select

from backend.config import (
    API_KEY_HMAC_SECRET,
    COOKIE_SAMESITE,
    COOKIE_SECURE,
    CSRF_SECRET_KEY,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    JWT_SECRET_KEY,
)

ACCESS_TOKEN_COOKIE_NAME = "access_token"
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"
CSRF_COOKIE_NAME = "csrf_token"
API_KEY_PREFIX = "kep_"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    now = datetime.utcnow()
    payload = data.copy()
    payload.update(
        {
            "exp": now + (expires_delta or timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)),
            "iat": now,
            "type": "access",
        }
    )
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    now = datetime.utcnow()
    payload = data.copy()
    payload.update(
        {
            "exp": now + (expires_delta or timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)),
            "iat": now,
            "type": "refresh",
        }
    )
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str, expected_type: str) -> dict:
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("Invalid token type")
    return payload


def _sign_csrf_value(value: str) -> str:
    signature = hmac.new(
        CSRF_SECRET_KEY.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{value}.{signature}"


def create_csrf_token() -> str:
    return _sign_csrf_value(secrets.token_urlsafe(32))


def verify_csrf_token(token: Optional[str], expected: Optional[str]) -> bool:
    if not token or not expected:
        return False
    return hmac.compare_digest(token, expected)


def _cookie_params(http_only: bool) -> dict:
    return {
        "httponly": http_only,
        "secure": COOKIE_SECURE,
        "samesite": COOKIE_SAMESITE,
        "path": "/",
    }


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    csrf_token: str,
) -> None:
    response.set_cookie(
        ACCESS_TOKEN_COOKIE_NAME,
        access_token,
        max_age=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **_cookie_params(True),
    )
    response.set_cookie(
        REFRESH_TOKEN_COOKIE_NAME,
        refresh_token,
        max_age=JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        **_cookie_params(True),
    )
    response.set_cookie(
        CSRF_COOKIE_NAME,
        csrf_token,
        max_age=JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        **_cookie_params(False),
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME, **_cookie_params(True))
    response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME, **_cookie_params(True))
    response.delete_cookie(CSRF_COOKIE_NAME, **_cookie_params(False))


def hash_api_key(plain_key: str) -> str:
    return hmac.new(
        API_KEY_HMAC_SECRET.encode("utf-8"),
        plain_key.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def generate_api_key() -> tuple[str, str, str]:
    random_part = secrets.token_urlsafe(32)
    plain_key = f"{API_KEY_PREFIX}{random_part}"
    return plain_key, plain_key[:16], hash_api_key(plain_key)


def get_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token

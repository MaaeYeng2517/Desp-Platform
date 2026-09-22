"""Application configuration."""
import json
import logging
import os
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent

APP_ENV = os.getenv("APP_ENV", "development").lower()
IS_PRODUCTION = APP_ENV in {"production", "prod"}
DEBUG = os.getenv("DEBUG", "false" if IS_PRODUCTION else "true").lower() == "true"
APP_NAME = os.getenv("APP_NAME", "Knowledge Engineering Platform")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://ke_user:ke_password@localhost:5432/knowledge_platform",
)
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "false").lower() == "true"
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "20"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
LLM_EMBEDDING_MODEL = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-3-small")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "development-only-change-me")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30"))

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", FRONTEND_URL).rstrip("/")
ALLOWED_ORIGINS_VALUE = os.getenv("ALLOWED_ORIGINS", FRONTEND_URL)
ALLOWED_ORIGINS = list(
    dict.fromkeys(
        origin.strip()
        for origin in ALLOWED_ORIGINS_VALUE.split(",")
        if origin.strip()
    )
)
if FRONTEND_URL not in ALLOWED_ORIGINS:
    ALLOWED_ORIGINS.insert(0, FRONTEND_URL)

ADMIN_EMAILS = [
    email.strip().lower()
    for email in os.getenv("ADMIN_EMAILS", "").split(",")
    if email.strip()
]
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true" if IS_PRODUCTION else "false").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax").lower()
if COOKIE_SAMESITE not in {"lax", "strict", "none"}:
    raise ValueError("COOKIE_SAMESITE must be lax, strict, or none")
CSRF_SECRET_KEY = os.getenv("CSRF_SECRET_KEY", "development-only-change-me")
API_KEY_HMAC_SECRET = os.getenv("API_KEY_HMAC_SECRET", "development-only-change-me")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_SUCCESS_URL = os.getenv(
    "STRIPE_SUCCESS_URL",
    f"{FRONTEND_URL}/billing?checkout=success",
)
STRIPE_CANCEL_URL = os.getenv(
    "STRIPE_CANCEL_URL",
    f"{FRONTEND_URL}/billing?checkout=cancelled",
)
STRIPE_FREE_PRICE_ID = os.getenv("STRIPE_FREE_PRICE_ID", "")
STRIPE_PRO_PRICE_ID = os.getenv("STRIPE_PRO_PRICE_ID", "")
STRIPE_ENTERPRISE_PRICE_ID = os.getenv("STRIPE_ENTERPRISE_PRICE_ID", "")


def _configured_plans() -> list[dict[str, Any]]:
    raw = os.getenv("SAAS_PLANS", "").strip()
    if raw:
        try:
            plans = json.loads(raw)
            if isinstance(plans, list) and plans:
                return plans
        except json.JSONDecodeError as exc:
            raise ValueError("SAAS_PLANS must be a JSON array") from exc

    return [
        {
            "code": "free",
            "name": "Free",
            "description": "เริ่มต้นใช้งานแพลตฟอร์มและ API พื้นฐาน",
            "price_cents": 0,
            "currency": "thb",
            "interval": "month",
            "api_calls_per_month": 1000,
            "features": ["basic_search", "basic_rag", "api_access"],
            "stripe_price_id": STRIPE_FREE_PRICE_ID,
            "sort_order": 0,
        },
        {
            "code": "pro",
            "name": "Pro",
            "description": "สำหรับทีมที่ต้องการขีดจำกัด API และ_workflow ที่ก้าวหน้าขึ้น",
            "price_cents": 29000,
            "currency": "thb",
            "interval": "month",
            "api_calls_per_month": 100000,
            "features": ["basic_search", "advanced_search", "rag", "api_access", "workflows", "usage_analytics"],
            "stripe_price_id": STRIPE_PRO_PRICE_ID,
            "sort_order": 10,
        },
        {
            "code": "enterprise",
            "name": "Enterprise",
            "description": "แผนสำหรับองค์กร พร้อมการผสานรวมและการสนับสนุนแบบเฉพาะ",
            "price_cents": 99000,
            "currency": "thb",
            "interval": "month",
            "api_calls_per_month": 1000000,
            "features": ["everything_in_pro", "custom_integrations", "sso", "audit_logs", "dedicated_support"],
            "stripe_price_id": STRIPE_ENTERPRISE_PRICE_ID,
            "sort_order": 20,
        },
    ]


MEMBERSHIP_PLANS = _configured_plans()


def validate_production_config() -> None:
    errors: list[str] = []
    if not IS_PRODUCTION:
        return

    if not JWT_SECRET_KEY or JWT_SECRET_KEY == "development-only-change-me":
        errors.append("JWT_SECRET_KEY must be set in production")
    if not CSRF_SECRET_KEY or CSRF_SECRET_KEY == "development-only-change-me":
        errors.append("CSRF_SECRET_KEY must be set in production")
    if not API_KEY_HMAC_SECRET or API_KEY_HMAC_SECRET == "development-only-change-me":
        errors.append("API_KEY_HMAC_SECRET must be set in production")
    if not STRIPE_SECRET_KEY:
        errors.append("STRIPE_SECRET_KEY must be set in production")
    if not STRIPE_WEBHOOK_SECRET:
        errors.append("STRIPE_WEBHOOK_SECRET must be set in production")
    if not COOKIE_SECURE:
        errors.append("COOKIE_SECURE must be true in production")
    if not ADMIN_EMAILS:
        errors.append("ADMIN_EMAILS must contain at least one administrator")
    if any(origin == "*" for origin in ALLOWED_ORIGINS):
        errors.append("Wildcard CORS origins are not allowed with credentials")

    paid_plans = [plan for plan in MEMBERSHIP_PLANS if int(plan.get("price_cents", 0)) > 0]
    if paid_plans and not all(plan.get("stripe_price_id") for plan in paid_plans):
        errors.append("Every paid plan requires a STRIPE_*_PRICE_ID or SAAS_PLANS price ID")

    if errors:
        raise RuntimeError("Production config validation failed: " + "; ".join(errors))

    logging.getLogger(__name__).info("Production configuration validated")

"""
Knowledge Engineering Platform - Backend Core
"""
import os
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://ke_user:ke_password@localhost:5432/knowledge_platform")

# MinIO
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Elasticsearch
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")

# Qdrant
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
LLM_EMBEDDING_MODEL = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-3-small")

# JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# App
APP_NAME = "Knowledge Engineering Platform"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Security
ADMIN_EMAILS = [e.strip() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()]
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")
CSRF_SECRET_KEY = os.getenv("CSRF_SECRET_KEY", "")

# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL", "http://localhost:3000/billing/success")
STRIPE_CANCEL_URL = os.getenv("STRIPE_CANCEL_URL", "http://localhost:3000/billing/cancel")

# API Key
API_KEY_HMAC_SECRET = os.getenv("API_KEY_HMAC_SECRET", "")

# Membership Plans (seeded from env or defaults)
MEMBERSHIP_PLANS = {
    "free": {"name": "Free", "price_cents": 0, "api_calls_per_month": 1000, "features": ["basic_search", "basic_rag"]},
    "pro": {"name": "Pro", "price_cents": 2900, "api_calls_per_month": 100000, "features": ["basic_search", "basic_rag", "advanced_search", "api_access", "workflows"]},
    "enterprise": {"name": "Enterprise", "price_cents": 9900, "api_calls_per_month": 1000000, "features": ["basic_search", "basic_rag", "advanced_search", "api_access", "workflows", "custom_integrations", "sso", "dedicated_support"]},
}

def validate_production_config():
    """Validate required production configuration"""
    errors = []
    warnings = []
    
    if not DEBUG:
        if not JWT_SECRET_KEY or JWT_SECRET_KEY == "your-secret-key-change-in-production":
            errors.append("JWT_SECRET_KEY must be set in production")
        if not CSRF_SECRET_KEY:
            errors.append("CSRF_SECRET_KEY must be set in production")
        if not API_KEY_HMAC_SECRET:
            errors.append("API_KEY_HMAC_SECRET must be set in production")
        if not STRIPE_SECRET_KEY:
            warnings.append("STRIPE_SECRET_KEY not set - billing features disabled")
        if not STRIPE_WEBHOOK_SECRET:
            warnings.append("STRIPE_WEBHOOK_SECRET not set - webhook verification disabled")
        if COOKIE_SECURE is False:
            warnings.append("COOKIE_SECURE should be true in production")
        if not ADMIN_EMAILS:
            warnings.append("ADMIN_EMAILS not set - no admin users will be created automatically")
    
    if errors:
        raise RuntimeError(f"Production config validation failed: {'; '.join(errors)}")
    
    for w in warnings:
        import logging
        logging.getLogger(__name__).warning(w)
    
    return True
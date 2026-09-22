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
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# App
APP_NAME = "Knowledge Engineering Platform"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
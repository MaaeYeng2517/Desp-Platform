"""Embedded Analytics Configuration."""
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Embedded Analytics"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "postgresql+asyncpg://dataeng:dataeng@localhost:5432/datawarehouse"
    DATABASE_ECHO: bool = False

    EMBED_BASE_URL: str = "http://localhost:8080"
    API_BASE_URL: str = "http://localhost:8080"

    ALLOWED_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])

    EMBED_TOKEN_SECRET: str = "change-me-in-production"
    DEFAULT_TOKEN_EXPIRY: int = 3600
    MAX_TOKEN_EXPIRY: int = 86400


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
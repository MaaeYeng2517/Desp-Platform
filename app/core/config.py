import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Data Core Platform"

    POSTGRES_HOST: str = os.getenv("DB_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("DB_PORT", "5432"))
    POSTGRES_USER: str = os.getenv("DB_USER", "dataeng")
    POSTGRES_PASSWORD: str = os.getenv("DB_PASSWORD", "dataeng")
    POSTGRES_DB: str = os.getenv("DB_NAME", "datawarehouse")
    DATABASE_URL: str = ""

    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"
    MINIO_BUCKET_BRONZE: str = "bronze"
    MINIO_BUCKET_SILVER: str = "silver"
    MINIO_BUCKET_GOLD: str = "gold"

    OPENLINEAGE_ENDPOINT: str = os.getenv("OPENLINEAGE_ENDPOINT", "http://localhost:5000")
    OPENLINEAGE_API_KEY: Optional[str] = os.getenv("OPENLINEAGE_API_KEY")
    OPENLINEAGE_NAMESPACE: str = os.getenv("OPENLINEAGE_NAMESPACE", "data-core-platform")

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    @property
    def async_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql+psycopg2://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )


settings = Settings()

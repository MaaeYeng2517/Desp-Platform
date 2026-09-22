"""Database configuration and session management."""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from backend.config import (
    DATABASE_ECHO,
    DATABASE_MAX_OVERFLOW,
    DATABASE_POOL_SIZE,
    DATABASE_URL,
)

Base = declarative_base()

engine = create_async_engine(
    DATABASE_URL,
    echo=DATABASE_ECHO,
    future=True,
    pool_size=DATABASE_POOL_SIZE,
    max_overflow=DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

from backend.app.models import (
    api_key,
    billing,
    chunk,
    contact,
    document,
    entity,
    evaluation,
    knowledge_base,
    metadata,
    source,
    tenant,
    user,
    workflow,
    relationship,
)


async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text(
                """
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS role VARCHAR(20)
                """
            )
        )
        await conn.execute(
            text(
                """
                UPDATE users
                SET role = 'member'
                WHERE role IS NULL
                """
            )
        )
        await conn.execute(
            text(
                """
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255)
                """
            )
        )

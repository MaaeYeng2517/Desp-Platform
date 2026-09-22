"""Embedded Analytics Models."""
import secrets
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from embedded.database import Base


class EmbedToken(Base):
    __tablename__ = "embed_tokens"
    __table_args__ = (
        Index("ix_embed_tokens_token", "token", unique=True),
        Index("ix_embed_tokens_dashboard_id", "dashboard_id"),
        Index("ix_embed_tokens_chart_id", "chart_id"),
        Index("ix_embed_tokens_expires_at", "expires_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, default=lambda: secrets.token_urlsafe(32))
    dashboard_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    chart_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @classmethod
    def create_token(
        cls,
        dashboard_id: str | None = None,
        chart_id: str | None = None,
        expires_in: int = 3600,
        domain: str | None = None,
    ) -> "EmbedToken":
        return cls(
            dashboard_id=dashboard_id,
            chart_id=chart_id,
            domain=domain,
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
        )


class EmbeddedDashboard(Base):
    __tablename__ = "embedded_dashboards"
    __table_args__ = (
        Index("ix_embedded_dashboards_is_active", "is_active"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    charts: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class EmbeddedChart(Base):
    __tablename__ = "embedded_charts"
    __table_args__ = (
        Index("ix_embedded_charts_is_active", "is_active"),
        Index("ix_embedded_charts_chart_type", "chart_type"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    chart_type: Mapped[str] = mapped_column(String(50), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
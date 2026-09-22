"""Billing models for SaaS memberships."""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database import Base


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAUSED = "paused"


class MembershipPlan(Base):
    __tablename__ = "membership_plans"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID, ForeignKey("tenants.id"), nullable=False, index=True)
    code = Column(String(50), nullable=False)
    stripe_price_id = Column(String(255), nullable=True)
    stripe_product_id = Column(String(255), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price_cents = Column(Integer, default=0, nullable=False)
    currency = Column(String(3), default="usd", nullable=False)
    interval = Column(String(20), default="month", nullable=False)
    api_calls_per_month = Column(Integer, default=1000, nullable=False)
    features = Column(JSON, default=list, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="membership_plans")
    subscriptions = relationship("Subscription", back_populates="plan")

    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_membership_plans_tenant_code"),)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(UUID, ForeignKey("membership_plans.id"), nullable=False, index=True)
    stripe_customer_id = Column(String(255), index=True)
    stripe_subscription_id = Column(String(255), unique=True, index=True)
    stripe_price_id = Column(String(255))
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.INCOMPLETE, nullable=False, index=True)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    canceled_at = Column(DateTime)
    trial_start = Column(DateTime)
    trial_end = Column(DateTime)
    data = Column("metadata", JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="subscriptions")
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("MembershipPlan", back_populates="subscriptions")

    @property
    def is_active(self) -> bool:
        return self.status in (SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING)

    @property
    def api_calls_limit(self) -> int:
        return self.plan.api_calls_per_month if self.plan else 1000

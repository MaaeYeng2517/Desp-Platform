"""Billing models: MembershipPlan, Subscription"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Enum as SQLEnum, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base
import enum


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    TRIALING = "trialing"
    PAUSED = "paused"


class MembershipPlan(Base):
    __tablename__ = "membership_plans"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID, ForeignKey("tenants.id"), nullable=False)
    stripe_price_id = Column(String, unique=True, index=True)
    stripe_product_id = Column(String)
    name = Column(String, nullable=False)
    description = Column(Text)
    price_cents = Column(Integer, default=0)
    currency = Column(String, default="usd")
    interval = Column(String, default="month")  # month, year
    api_calls_per_month = Column(Integer, default=1000)
    features = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="membership_plans")
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    plan_id = Column(UUID, ForeignKey("membership_plans.id"), nullable=False)
    stripe_customer_id = Column(String, index=True)
    stripe_subscription_id = Column(String, unique=True, index=True)
    stripe_price_id = Column(String)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.INCOMPLETE, nullable=False)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime)
    trial_start = Column(DateTime)
    trial_end = Column(DateTime)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="subscriptions")
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("MembershipPlan", back_populates="subscriptions")

    @property
    def is_active(self) -> bool:
        return self.status in (SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING)

    @property
    def api_calls_limit(self) -> int:
        return self.plan.api_calls_per_month if self.plan else 1000
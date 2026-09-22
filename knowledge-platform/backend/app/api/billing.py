"""Stripe billing and membership API."""
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.dependencies import require_active_membership, require_admin, require_platform_user
from backend.app.models.billing import MembershipPlan, Subscription, SubscriptionStatus
from backend.app.models.user import User
from backend.app.schemas import (
    AdminStatsResponse,
    EntitlementResponse,
    MembershipPlanCreate,
    MembershipPlanResponse,
    StripeCheckoutRequest,
    StripeCheckoutResponse,
    StripePortalRequest,
    StripePortalResponse,
    SubscriptionResponse,
    SubscriptionUpdate,
)
from backend.config import (
    MEMBERSHIP_PLANS,
    PUBLIC_BASE_URL,
    STRIPE_CANCEL_URL,
    STRIPE_SECRET_KEY,
    STRIPE_SUCCESS_URL,
    STRIPE_WEBHOOK_SECRET,
)
from backend.database import get_db

router = APIRouter()


def _stripe():
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Billing is not configured")
    import stripe

    stripe.api_key = STRIPE_SECRET_KEY
    return stripe


async def seed_default_plans(db: AsyncSession, tenant_id) -> None:
    configured_codes = set()
    for index, plan_data in enumerate(MEMBERSHIP_PLANS):
        code = str(plan_data.get("code", "")).strip().lower()
        if not code:
            continue
        configured_codes.add(code)
        result = await db.execute(
            select(MembershipPlan).where(
                MembershipPlan.tenant_id == tenant_id,
                MembershipPlan.code == code,
            )
        )
        plan = result.scalar_one_or_none()
        values = {
            "tenant_id": tenant_id,
            "code": code,
            "stripe_price_id": plan_data.get("stripe_price_id") or None,
            "stripe_product_id": plan_data.get("stripe_product_id") or None,
            "name": str(plan_data.get("name", code.title())),
            "description": plan_data.get("description"),
            "price_cents": int(plan_data.get("price_cents", 0)),
            "currency": str(plan_data.get("currency", "thb"))[:3].lower(),
            "interval": str(plan_data.get("interval", "month")),
            "api_calls_per_month": int(plan_data.get("api_calls_per_month", 1000)),
            "features": plan_data.get("features", []),
            "is_active": bool(plan_data.get("is_active", True)),
            "sort_order": int(plan_data.get("sort_order", index * 10)),
        }
        if plan:
            for field, value in values.items():
                setattr(plan, field, value)
        else:
            db.add(MembershipPlan(**values))
    await db.commit()


async def _get_plan(db: AsyncSession, user: User, plan_id) -> MembershipPlan:
    result = await db.execute(
        select(MembershipPlan).where(
            MembershipPlan.id == plan_id,
            MembershipPlan.tenant_id == user.tenant_id,
            MembershipPlan.is_active.is_(True),
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Membership plan not found")
    return plan


async def _get_subscription(db: AsyncSession, user: User) -> Optional[Subscription]:
    result = await db.execute(
        select(Subscription)
        .options(selectinload(Subscription.plan))
        .where(Subscription.user_id == user.id)
        .order_by(Subscription.created_at.desc())
    )
    return result.scalars().first()


def _utc_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=None) if value.tzinfo else value
    return datetime.fromtimestamp(int(value), tz=timezone.utc).replace(tzinfo=None)


def _status(value: Any) -> SubscriptionStatus:
    try:
        return SubscriptionStatus(str(value))
    except ValueError:
        return SubscriptionStatus.INCOMPLETE


async def _upsert_stripe_subscription(
    db: AsyncSession,
    stripe_subscription: dict,
    fallback_metadata: Optional[dict] = None,
) -> Subscription:
    metadata = stripe_subscription.get("metadata") or fallback_metadata or {}
    subscription_id = stripe_subscription.get("id")
    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    customer_id = stripe_subscription.get("customer")
    user_id = metadata.get("user_id")
    tenant_id = metadata.get("tenant_id")
    plan_id = metadata.get("plan_id")

    if not subscription:
        if not user_id or not tenant_id or not plan_id:
            price_id = None
            if stripe_subscription.get("items", {}).get("data"):
                price_id = stripe_subscription["items"]["data"][0].get("price", {}).get("id")
            if price_id:
                plan_result = await db.execute(
                    select(MembershipPlan).where(MembershipPlan.stripe_price_id == price_id)
                )
                plan = plan_result.scalar_one_or_none()
                if plan:
                    tenant_id = str(plan.tenant_id)
                    plan_id = str(plan.id)
        if not user_id or not tenant_id or not plan_id:
            return None
        subscription = Subscription(
            user_id=user_id,
            tenant_id=tenant_id,
            plan_id=plan_id,
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id,
            status=SubscriptionStatus.INCOMPLETE,
            metadata={"source": "stripe"},
        )
        db.add(subscription)
    else:
        if user_id:
            subscription.user_id = user_id
        if tenant_id:
            subscription.tenant_id = tenant_id
        if plan_id:
            subscription.plan_id = plan_id
        if customer_id:
            subscription.stripe_customer_id = customer_id

    subscription.stripe_price_id = (
        stripe_subscription.get("items", {}).get("data", [{}])[0].get("price", {}).get("id")
        if stripe_subscription.get("items", {}).get("data")
        else None
    )
    subscription.status = _status(stripe_subscription.get("status"))
    subscription.current_period_start = _utc_datetime(stripe_subscription.get("current_period_start"))
    subscription.current_period_end = _utc_datetime(stripe_subscription.get("current_period_end"))
    subscription.cancel_at_period_end = bool(stripe_subscription.get("cancel_at_period_end", False))
    subscription.canceled_at = _utc_datetime(stripe_subscription.get("canceled_at"))
    subscription.trial_start = _utc_datetime(stripe_subscription.get("trial_start"))
    subscription.trial_end = _utc_datetime(stripe_subscription.get("trial_end"))
    subscription.metadata = dict(metadata)
    await db.commit()

    if customer_id:
        user_result = await db.execute(select(User).where(User.id == subscription.user_id))
        member = user_result.scalar_one_or_none()
        if member:
            member.stripe_customer_id = customer_id
            await db.commit()
    return subscription


@router.get("/plans", response_model=list[MembershipPlanResponse])
async def list_plans(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MembershipPlan)
        .where(MembershipPlan.is_active.is_(True))
        .order_by(MembershipPlan.sort_order)
    )
    return result.scalars().all()


@router.post("/plans", response_model=MembershipPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: MembershipPlanCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    plan = MembershipPlan(tenant_id=user.tenant_id, **plan_data.model_dump())
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


@router.post("/checkout", response_model=StripeCheckoutResponse)
async def create_checkout_session(
    request_data: StripeCheckoutRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_active_membership),
):
    plan = await _get_plan(db, user, request_data.plan_id)
    if plan.price_cents <= 0:
        subscription = await _get_subscription(db, user)
        if not subscription or not subscription.is_active:
            raise HTTPException(status_code=403, detail="Membership is not active")
        return StripeCheckoutResponse(message="แผนฟรีเปิดใช้งานแล้ว")

    stripe = _stripe()
    subscription = await _get_subscription(db, user)
    customer_id = subscription.stripe_customer_id if subscription else None
    if not customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            metadata={"user_id": str(user.id), "tenant_id": str(user.tenant_id)},
        )
        customer_id = customer.id
        if subscription:
            subscription.stripe_customer_id = customer_id
        else:
            subscription = Subscription(
                tenant_id=user.tenant_id,
                user_id=user.id,
                plan_id=plan.id,
                stripe_customer_id=customer_id,
                status=SubscriptionStatus.INCOMPLETE,
                metadata={"source": "checkout"},
            )
            db.add(subscription)
        user.stripe_customer_id = customer_id
        await db.commit()

    success_url = request_data.success_url or STRIPE_SUCCESS_URL
    cancel_url = request_data.cancel_url or STRIPE_CANCEL_URL
    if "{" not in success_url:
        separator = "&" if "?" in success_url else "?"
        success_url = f"{success_url}{separator}session_id={{CHECKOUT_SESSION_ID}}"
    try:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            line_items=[{"price": plan.stripe_price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": str(user.id),
                "tenant_id": str(user.tenant_id),
                "plan_id": str(plan.id),
            },
            subscription_data={
                "metadata": {
                    "user_id": str(user.id),
                    "tenant_id": str(user.tenant_id),
                    "plan_id": str(plan.id),
                }
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Stripe checkout failed: {exc}") from exc

    if not session.url:
        raise HTTPException(status_code=502, detail="Stripe did not return a checkout URL")
    return StripeCheckoutResponse(checkout_url=session.url, session_id=session.id)


@router.post("/portal", response_model=StripePortalResponse)
async def create_portal_session(
    request_data: StripePortalRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_active_membership),
):
    subscription = await _get_subscription(db, user)
    if not subscription or not subscription.stripe_customer_id or not subscription.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No active billing subscription found")
    stripe = _stripe()
    try:
        session = stripe.billing_portal.Session.create(
            customer=subscription.stripe_customer_id,
            return_url=request_data.return_url or f"{PUBLIC_BASE_URL}/billing",
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Stripe portal failed: {exc}") from exc
    return StripePortalResponse(portal_url=session.url)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Stripe webhook is not configured")
    stripe = _stripe()
    signature = request.headers.get("stripe-signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, signature, STRIPE_WEBHOOK_SECRET)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature") from exc

    event_type = event.get("type")
    event_object = event.get("data", {}).get("object", {})
    if event_type == "checkout.session.completed":
        session_id = event_object.get("id")
        stripe_session = stripe.checkout.Session.retrieve(session_id)
        if stripe_session.get("subscription"):
            stripe_subscription = stripe.Subscription.retrieve(stripe_session["subscription"])
            await _upsert_stripe_subscription(
                db,
                stripe_subscription,
                dict(stripe_session.get("metadata") or {}),
            )
    elif event_type == "customer.subscription.created":
        await _upsert_stripe_subscription(db, event_object)
    elif event_type in {"customer.subscription.updated", "customer.subscription.deleted"}:
        await _upsert_stripe_subscription(db, event_object)
    elif event_type == "invoice.payment_failed":
        subscription_id = event_object.get("subscription")
        if subscription_id:
            result = await db.execute(
                select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
            )
            subscription = result.scalar_one_or_none()
            if subscription:
                subscription.status = SubscriptionStatus.PAST_DUE
                await db.commit()
    return {"received": True}


@router.get("/subscription", response_model=Optional[SubscriptionResponse])
async def get_my_subscription(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_user),
):
    return await _get_subscription(db, user)


@router.patch("/subscription", response_model=SubscriptionResponse)
async def update_subscription(
    update: SubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_active_membership),
):
    subscription = await _get_subscription(db, user)
    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="Active subscription not found")
    stripe = _stripe()
    try:
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=update.cancel_at_period_end,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Stripe update failed: {exc}") from exc
    subscription.cancel_at_period_end = bool(update.cancel_at_period_end)
    await db.commit()
    await db.refresh(subscription)
    return subscription


@router.get("/entitlement", response_model=EntitlementResponse)
async def get_entitlement(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_user),
):
    subscription = await _get_subscription(db, user)
    if subscription and subscription.is_active and subscription.plan:
        return EntitlementResponse(
            plan=subscription.plan.name,
            status=subscription.status.value,
            api_calls_limit=subscription.api_calls_limit,
            features=subscription.plan.features or [],
            current_period_end=subscription.current_period_end,
        )
    result = await db.execute(
        select(MembershipPlan).where(
            MembershipPlan.tenant_id == user.tenant_id,
            MembershipPlan.code == "free",
        )
    )
    plan = result.scalar_one_or_none()
    return EntitlementResponse(
        plan=plan.name if plan else "Free",
        status="inactive" if not subscription else subscription.status.value,
        api_calls_limit=plan.api_calls_per_month if plan else 1000,
        features=plan.features if plan else [],
    )

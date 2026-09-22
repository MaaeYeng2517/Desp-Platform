"""Billing API endpoints - Stripe integration"""
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from typing import Optional
import stripe

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from backend.config import (
    STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET,
    STRIPE_SUCCESS_URL, STRIPE_CANCEL_URL
)
from backend.database import get_db
from backend.app.models.user import User
from backend.app.models.tenant import Tenant
from backend.app.models.billing import MembershipPlan, Subscription, SubscriptionStatus
from backend.app.schemas import (
    MembershipPlanCreate, MembershipPlanResponse,
    SubscriptionCreate, SubscriptionResponse, SubscriptionUpdate,
    StripeCheckoutRequest, StripeCheckoutResponse,
    StripePortalRequest, StripePortalResponse,
    AdminStatsResponse
)
from backend.app.api.auth import get_current_user, require_admin, require_platform_access

router = APIRouter()

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY


async def seed_default_plans(db: AsyncSession, tenant_id: str):
    """Seed default membership plans for a tenant"""
    from backend.config import MEMBERSHIP_PLANS
    
    for key, plan_data in MEMBERSHIP_PLANS.items():
        existing = await db.execute(
            select(MembershipPlan).where(
                MembershipPlan.tenant_id == tenant_id,
                MembershipPlan.name == plan_data["name"]
            )
        )
        if not existing.scalar_one_or_none():
            plan = MembershipPlan(
                tenant_id=tenant_id,
                name=plan_data["name"],
                description=f"{plan_data['name']} plan",
                price_cents=plan_data["price_cents"],
                api_calls_per_month=plan_data["api_calls_per_month"],
                features=plan_data["features"],
                is_active=True,
                sort_order=list(MEMBERSHIP_PLANS.keys()).index(key)
            )
            db.add(plan)
    await db.commit()


@router.on_event("startup")
async def startup_seed_plans():
    """Seed plans on startup"""
    from backend.database import async_session_factory
    async with async_session_factory() as db:
        tenants_result = await db.execute(select(Tenant).where(Tenant.is_active == True))
        for tenant in tenants_result.scalars().all():
            await seed_default_plans(db, str(tenant.id))


@router.get("/plans", response_model=list[MembershipPlanResponse])
async def list_plans(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_access)
):
    """List membership plans for current tenant"""
    result = await db.execute(
        select(MembershipPlan)
        .where(MembershipPlan.tenant_id == user.tenant_id, MembershipPlan.is_active == True)
        .order_by(MembershipPlan.sort_order)
    )
    return result.scalars().all()


@router.post("/plans", response_model=MembershipPlanResponse, status_code=201)
async def create_plan(
    plan_data: MembershipPlanCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin)
):
    """Create a new membership plan (admin only)"""
    plan = MembershipPlan(
        tenant_id=user.tenant_id,
        **plan_data.model_dump()
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


@router.post("/checkout", response_model=StripeCheckoutResponse)
async def create_checkout_session(
    request: StripeCheckoutRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_access)
):
    """Create Stripe Checkout session for subscription"""
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Billing not configured")
    
    plan_result = await db.execute(
        select(MembershipPlan).where(
            MembershipPlan.id == request.plan_id,
            MembershipPlan.tenant_id == user.tenant_id
        )
    )
    plan = plan_result.scalar_one_or_none()
    if not plan or not plan.stripe_price_id:
        raise HTTPException(status_code=400, detail="Invalid plan or plan not configured for Stripe")
    
    customer_id = None
    sub_result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.stripe_customer_id.is_not(None)
        ).order_by(Subscription.created_at.desc())
    )
    existing_sub = sub_result.scalar_one_or_none()
    if existing_sub:
        customer_id = existing_sub.stripe_customer_id
    
    try:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            customer_email=user.email if not customer_id else None,
            payment_method_types=["card"],
            line_items=[{"price": plan.stripe_price_id, "quantity": 1}],
            mode="subscription",
            success_url=request.success_url or STRIPE_SUCCESS_URL,
            cancel_url=request.cancel_url or STRIPE_CANCEL_URL,
            metadata={
                "user_id": str(user.id),
                "tenant_id": str(user.tenant_id),
                "plan_id": str(plan.id)
            },
            subscription_data={
                "metadata": {
                    "user_id": str(user.id),
                    "tenant_id": str(user.tenant_id),
                    "plan_id": str(plan.id)
                }
            } if not customer_id else None
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return StripeCheckoutResponse(checkout_url=session.url, session_id=session.id)


@router.post("/portal", response_model=StripePortalResponse)
async def create_portal_session(
    request: StripePortalRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_access)
):
    """Create Stripe Customer Portal session"""
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Billing not configured")
    
    sub_result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.stripe_customer_id.is_not(None)
        ).order_by(Subscription.created_at.desc())
    )
    subscription = sub_result.scalar_one_or_none()
    
    if not subscription or not subscription.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account found")
    
    try:
        session = stripe.billing_portal.Session.create(
            customer=subscription.stripe_customer_id,
            return_url=request.return_url or STRIPE_SUCCESS_URL
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return StripePortalResponse(portal_url=session.url)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature")
):
    """Handle Stripe webhook events"""
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Webhook not configured")
    
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await handle_checkout_completed(db, session)
    elif event["type"] == "customer.subscription.created":
        subscription = event["data"]["object"]
        await handle_subscription_created(db, subscription)
    elif event["type"] in ("customer.subscription.updated", "customer.subscription.deleted"):
        subscription = event["data"]["object"]
        await handle_subscription_updated(db, subscription)
    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        await handle_payment_failed(db, invoice)
    
    return {"received": True}


async def handle_checkout_completed(db: AsyncSession, session: dict):
    """Handle successful checkout"""
    user_id = session["metadata"].get("user_id")
    tenant_id = session["metadata"].get("tenant_id")
    plan_id = session["metadata"].get("plan_id")
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    
    if not all([user_id, tenant_id, plan_id, customer_id]):
        return
    
    sub = Subscription(
        tenant_id=tenant_id,
        user_id=user_id,
        plan_id=plan_id,
        stripe_customer_id=customer_id,
        stripe_subscription_id=subscription_id,
        status=SubscriptionStatus.INCOMPLETE,
        metadata={"checkout_session_id": session["id"]}
    )
    db.add(sub)
    await db.commit()


async def handle_subscription_created(db: AsyncSession, stripe_sub: dict):
    """Handle subscription created"""
    user_id = stripe_sub["metadata"].get("user_id")
    tenant_id = stripe_sub["metadata"].get("tenant_id")
    plan_id = stripe_sub["metadata"].get("plan_id")
    customer_id = stripe_sub["customer"]
    
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_sub["id"]
        )
    )
    sub = result.scalar_one_or_none()
    
    if not sub:
        sub = Subscription(
            tenant_id=tenant_id,
            user_id=user_id,
            plan_id=plan_id,
            stripe_customer_id=customer_id,
            stripe_subscription_id=stripe_sub["id"],
            stripe_price_id=stripe_sub["items"]["data"][0]["price"]["id"] if stripe_sub["items"]["data"] else None
        )
        db.add(sub)
    
    sub.status = SubscriptionStatus(stripe_sub["status"])
    sub.current_period_start = datetime.utcfromtimestamp(stripe_sub["current_period_start"])
    sub.current_period_end = datetime.utcfromtimestamp(stripe_sub["current_period_end"])
    sub.cancel_at_period_end = stripe_sub.get("cancel_at_period_end", False)
    
    if stripe_sub.get("trial_start"):
        sub.trial_start = datetime.utcfromtimestamp(stripe_sub["trial_start"])
    if stripe_sub.get("trial_end"):
        sub.trial_end = datetime.utcfromtimestamp(stripe_sub["trial_end"])
    
    await db.commit()


async def handle_subscription_updated(db: AsyncSession, stripe_sub: dict):
    """Handle subscription updated/deleted"""
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_sub["id"]
        )
    )
    sub = result.scalar_one_or_none()
    if not sub:
        return
    
    sub.status = SubscriptionStatus(stripe_sub["status"])
    sub.current_period_start = datetime.utcfromtimestamp(stripe_sub["current_period_start"])
    sub.current_period_end = datetime.utcfromtimestamp(stripe_sub["current_period_end"])
    sub.cancel_at_period_end = stripe_sub.get("cancel_at_period_end", False)
    sub.canceled_at = datetime.utcfromtimestamp(stripe_sub["canceled_at"]) if stripe_sub.get("canceled_at") else None
    sub.stripe_price_id = stripe_sub["items"]["data"][0]["price"]["id"] if stripe_sub["items"]["data"] else None
    
    await db.commit()


async def handle_payment_failed(db: AsyncSession, invoice: dict):
    """Handle failed payment"""
    subscription_id = invoice.get("subscription")
    if not subscription_id:
        return
    
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == subscription_id
        )
    )
    sub = result.scalar_one_or_none()
    if sub:
        sub.status = SubscriptionStatus.PAST_DUE
        await db.commit()


from datetime import datetime

@router.get("/subscription", response_model=Optional[SubscriptionResponse])
async def get_my_subscription(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_access)
):
    """Get current user's subscription"""
    result = await db.execute(
        select(Subscription)
        .options(selectinload(Subscription.plan))
        .where(Subscription.user_id == user.id)
        .order_by(Subscription.created_at.desc())
    )
    return result.scalars().first()


@router.patch("/subscription", response_model=SubscriptionResponse)
async def update_subscription(
    update: SubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_access)
):
    """Update subscription (e.g., cancel at period end)"""
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Billing not configured")
    
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING, SubscriptionStatus.PAST_DUE])
        ).order_by(Subscription.created_at.desc())
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription")
    
    if update.cancel_at_period_end is not None:
        try:
            stripe.Subscription.modify(
                sub.stripe_subscription_id,
                cancel_at_period_end=update.cancel_at_period_end
            )
            sub.cancel_at_period_end = update.cancel_at_period_end
            await db.commit()
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    return sub


@router.get("/entitlement")
async def get_entitlement(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_access)
):
    """Get current user's entitlement (plan features and limits)"""
    result = await db.execute(
        select(Subscription)
        .options(selectinload(Subscription.plan))
        .where(Subscription.user_id == user.id)
        .order_by(Subscription.created_at.desc())
    )
    sub = result.scalars().first()
    
    if not sub or not sub.is_active:
        plan_result = await db.execute(
            select(MembershipPlan).where(
                MembershipPlan.tenant_id == user.tenant_id,
                MembershipPlan.name == "Free"
            )
        )
        plan = plan_result.scalar_one_or_none()
        if not plan:
            plan = MembershipPlan(name="Free", price_cents=0, api_calls_per_month=1000, features=["basic_search"])
        return {
            "plan": plan.name if plan else "Free",
            "status": "inactive",
            "api_calls_limit": plan.api_calls_per_month if plan else 1000,
            "features": plan.features if plan else ["basic_search"]
        }
    
    return {
        "plan": sub.plan.name if sub.plan else "Unknown",
        "status": sub.status.value,
        "api_calls_limit": sub.api_calls_limit,
        "features": sub.plan.features if sub.plan else [],
        "current_period_end": sub.current_period_end
    }
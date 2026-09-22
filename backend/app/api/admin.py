"""Admin API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from backend.database import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.tenant import Tenant
from backend.app.models.billing import Subscription, SubscriptionStatus, MembershipPlan
from backend.app.models.api_key import ApiKey, ApiUsageLog
from backend.app.models.contact import ContactMessage, ContactStatus
from backend.app.schemas import (
    AdminStatsResponse, AdminUserListResponse, AdminTenantListResponse,
    UserResponse, TenantResponse, UserUpdate, UserRole as SchemaUserRole
)
from backend.app.dependencies import require_admin

router = APIRouter()


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get platform statistics"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    total_users = await db.scalar(select(func.count(User.id)))
    total_tenants = await db.scalar(select(func.count(Tenant.id)))
    total_subscriptions = await db.scalar(select(func.count(Subscription.id)))
    active_subscriptions = await db.scalar(
        select(func.count(Subscription.id)).where(
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING])
        )
    )
    total_api_keys = await db.scalar(select(func.count(ApiKey.id)))
    active_api_keys = await db.scalar(
        select(func.count(ApiKey.id)).where(ApiKey.is_active == True)
    )
    total_api_calls_today = await db.scalar(
        select(func.count(ApiUsageLog.id)).where(ApiUsageLog.created_at >= today_start)
    )
    total_api_calls_month = await db.scalar(
        select(func.count(ApiUsageLog.id)).where(ApiUsageLog.created_at >= month_start)
    )
    revenue_result = await db.execute(
        select(func.sum(MembershipPlan.price_cents))
        .join(Subscription, Subscription.plan_id == MembershipPlan.id)
        .where(Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]))
    )
    revenue_cents = revenue_result.scalar() or 0
    contact_messages = await db.scalar(select(func.count(ContactMessage.id)))
    pending_contact_messages = await db.scalar(
        select(func.count(ContactMessage.id)).where(ContactMessage.status == ContactStatus.NEW)
    )
    
    return AdminStatsResponse(
        total_users=total_users,
        total_tenants=total_tenants,
        total_subscriptions=total_subscriptions,
        active_subscriptions=active_subscriptions,
        total_api_keys=total_api_keys,
        active_api_keys=active_api_keys,
        total_api_calls_today=total_api_calls_today,
        total_api_calls_month=total_api_calls_month,
        revenue_cents=revenue_cents,
        contact_messages=contact_messages,
        pending_contact_messages=pending_contact_messages
    )


@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    tenant_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all users with pagination and filters"""
    query = select(User).options(selectinload(User.tenant))
    
    if search:
        query = query.where(
            or_(User.email.ilike(f"%{search}%"), User.full_name.ilike(f"%{search}%"))
        )
    if role:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if tenant_id:
        query = query.where(User.tenant_id == tenant_id)
    
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    
    query = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return AdminUserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get user by ID"""
    result = await db.execute(
        select(User).options(selectinload(User.tenant)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update user (role, active status, etc.)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == admin.id and update.role and update.role != user.role:
        raise HTTPException(status_code=400, detail="Cannot change own role")
    
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete user"""
    if user_id == str(admin.id):
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted"}


@router.get("/tenants", response_model=AdminTenantListResponse)
async def list_tenants(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all tenants with pagination and filters"""
    query = select(Tenant)
    
    if search:
        query = query.where(
            or_(Tenant.name.ilike(f"%{search}%"), Tenant.slug.ilike(f"%{search}%"))
        )
    if is_active is not None:
        query = query.where(Tenant.is_active == is_active)
    
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    
    query = query.order_by(Tenant.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    tenants = result.scalars().all()
    
    return AdminTenantListResponse(
        tenants=[TenantResponse.model_validate(t) for t in tenants],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get tenant by ID"""
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return TenantResponse.model_validate(tenant)


@router.patch("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update tenant status"""
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if is_active is not None:
        tenant.is_active = is_active
        tenant.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(tenant)
    
    return TenantResponse.model_validate(tenant)


@router.get("/subscriptions")
async def list_subscriptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[SubscriptionStatus] = None,
    tenant_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all subscriptions"""
    query = select(Subscription).options(
        selectinload(Subscription.user), selectinload(Subscription.plan), selectinload(Subscription.tenant)
    )
    
    if status:
        query = query.where(Subscription.status == status)
    if tenant_id:
        query = query.where(Subscription.tenant_id == tenant_id)
    
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    
    query = query.order_by(Subscription.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    subscriptions = result.scalars().all()
    
    return {
        "subscriptions": [
            {
                "id": str(s.id),
                "user": {"id": str(s.user.id), "email": s.user.email} if s.user else None,
                "tenant": {"id": str(s.tenant.id), "name": s.tenant.name} if s.tenant else None,
                "plan": {"id": str(s.plan.id), "name": s.plan.name} if s.plan else None,
                "status": s.status.value,
                "current_period_end": s.current_period_end,
                "cancel_at_period_end": s.cancel_at_period_end
            }
            for s in subscriptions
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/api-keys")
async def list_all_api_keys(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tenant_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List all API keys"""
    query = select(ApiKey).options(selectinload(ApiKey.user), selectinload(ApiKey.tenant))
    
    if tenant_id:
        query = query.where(ApiKey.tenant_id == tenant_id)
    if is_active is not None:
        query = query.where(ApiKey.is_active == is_active)
    
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    
    query = query.order_by(ApiKey.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    keys = result.scalars().all()
    
    return {
        "api_keys": [
            {
                "id": str(k.id),
                "name": k.name,
                "prefix": k.key_prefix,
                "user": {"id": str(k.user.id), "email": k.user.email} if k.user else None,
                "tenant": {"id": str(k.tenant.id), "name": k.tenant.name} if k.tenant else None,
                "scopes": k.scopes,
                "is_active": k.is_active,
                "last_used_at": k.last_used_at,
                "created_at": k.created_at
            }
            for k in keys
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.delete("/api-keys/{key_id}")
async def revoke_any_api_key(
    key_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Revoke any API key"""
    result = await db.execute(select(ApiKey).where(ApiKey.id == key_id))
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    key.is_active = False
    await db.commit()
    return {"message": "API key revoked"}


@router.get("/contact-messages")
async def list_contact_messages(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[ContactStatus] = None,
    tenant_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """List contact messages"""
    query = select(ContactMessage).options(
        selectinload(ContactMessage.user), selectinload(ContactMessage.tenant), selectinload(ContactMessage.resolver)
    )
    
    if status:
        query = query.where(ContactMessage.status == status)
    if tenant_id:
        query = query.where(ContactMessage.tenant_id == tenant_id)
    
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    
    query = query.order_by(ContactMessage.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return {
        "messages": [
            {
                "id": str(m.id),
                "name": m.name,
                "email": m.email,
                "subject": m.subject,
                "status": m.status.value,
                "user": {"id": str(m.user.id), "email": m.user.email} if m.user else None,
                "tenant": {"id": str(m.tenant.id), "name": m.tenant.name} if m.tenant else None,
                "created_at": m.created_at,
                "resolved_at": m.resolved_at
            }
            for m in messages
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.patch("/contact-messages/{message_id}")
async def update_contact_message(
    message_id: str,
    status: Optional[ContactStatus] = None,
    admin_notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update contact message status"""
    result = await db.execute(select(ContactMessage).where(ContactMessage.id == message_id))
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if status:
        message.status = status
        if status == ContactStatus.RESOLVED:
            message.resolved_at = datetime.utcnow()
            message.resolved_by = admin.id
    if admin_notes:
        message.admin_notes = admin_notes
    
    message.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(message)
    return {"message": "Updated"}
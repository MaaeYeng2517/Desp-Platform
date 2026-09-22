"""Public contact form endpoint"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.app.models.user import User
from backend.app.models.tenant import Tenant
from backend.app.models.contact import ContactMessage, ContactStatus
from backend.app.schemas import ContactMessageCreate, ContactMessageResponse
from backend.app.api.auth import get_current_user_optional

router = APIRouter()


@router.post("/contact", response_model=ContactMessageResponse, status_code=201)
async def create_contact_message(
    message_data: ContactMessageCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    """Submit a contact message (public endpoint)"""
    tenant_id = None
    if user:
        tenant_id = user.tenant_id
    else:
        # Try to get tenant from origin/header for unauthenticated requests
        origin = request.headers.get("origin") or request.headers.get("referer")
        if origin:
            from urllib.parse import urlparse
            domain = urlparse(origin).netloc
            if domain:
                result = await db.execute(select(Tenant).where(Tenant.slug == domain))
                tenant = result.scalar_one_or_none()
                if tenant:
                    tenant_id = tenant.id
    
    message = ContactMessage(
        user_id=user.id if user else None,
        tenant_id=tenant_id,
        name=message_data.name,
        email=message_data.email,
        subject=message_data.subject,
        message=message_data.message,
        status=ContactStatus.NEW,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return ContactMessageResponse.model_validate(message)


@router.get("/contact/{message_id}", response_model=ContactMessageResponse)
async def get_contact_message(
    message_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_optional)
):
    """Get contact message by ID (user can only see their own, admins see all)"""
    result = await db.execute(
        select(ContactMessage).where(ContactMessage.id == message_id)
    )
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if user and message.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this message")
    
    return ContactMessageResponse.model_validate(message)
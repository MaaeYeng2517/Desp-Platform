"""Public contact form endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.dependencies import get_current_user_optional
from backend.app.models.contact import ContactMessage, ContactStatus
from backend.app.models.user import User, UserRole
from backend.app.schemas import ContactMessageCreate, ContactMessageResponse
from backend.database import get_db

router = APIRouter()


@router.post("/contact", response_model=ContactMessageResponse, status_code=status.HTTP_201_CREATED)
async def create_contact_message(
    message_data: ContactMessageCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    message = ContactMessage(
        user_id=user.id if user else None,
        tenant_id=user.tenant_id if user else None,
        name=message_data.name.strip(),
        email=str(message_data.email).strip().lower(),
        subject=message_data.subject.strip(),
        message=message_data.message.strip(),
        status=ContactStatus.NEW,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return ContactMessageResponse.model_validate(message)


@router.get("/contact/{message_id}", response_model=ContactMessageResponse)
async def get_contact_message(
    message_id,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    result = await db.execute(select(ContactMessage).where(ContactMessage.id == message_id))
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Contact message not found")
    if user and message.user_id != user.id and user.role != UserRole.ADMIN and not user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to view this message")
    return ContactMessageResponse.model_validate(message)

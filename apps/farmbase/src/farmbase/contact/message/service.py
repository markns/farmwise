from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Message
from .schemas import MessageCreate, MessageUpdate


async def get(*, db_session: AsyncSession, contact_id: int, since: datetime = datetime.min) -> Sequence[Message]:
    """Returns messages for a contact since a given datetime."""
    result = await db_session.execute(
        select(Message)
        .options(selectinload(Message.contact))
        .where(Message.contact_id == contact_id, Message.created_at > since)
        .order_by(Message.created_at.desc())
    )
    return result.scalars().all()


async def get_by_id(*, db_session: AsyncSession, message_id: int) -> Message | None:
    """Returns a message by ID."""
    result = await db_session.execute(
        select(Message)
        .options(selectinload(Message.contact))
        .where(Message.id == message_id)
    )
    return result.scalar_one_or_none()


async def get_by_whatsapp_id(*, db_session: AsyncSession, whatsapp_message_id: str) -> Message | None:
    """Returns a message by WhatsApp message ID."""
    result = await db_session.execute(
        select(Message)
        .options(selectinload(Message.contact))
        .where(Message.whatsapp_message_id == whatsapp_message_id)
    )
    return result.scalar_one_or_none()


async def create(*, db_session: AsyncSession, message_in: MessageCreate) -> Message:
    """Creates a new message."""
    message = Message(**message_in.model_dump())
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)
    return message


async def update(*, db_session: AsyncSession, message: Message, message_update: MessageUpdate) -> Message:
    """Updates an existing message."""
    update_data = message_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(message, field, value)
    
    await db_session.commit()
    await db_session.refresh(message)
    return message


async def list_messages(
    *, 
    db_session: AsyncSession, 
    contact_id: Optional[int] = None,
    message_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Sequence[Message]:
    """Lists messages with optional filtering."""
    query = select(Message).options(selectinload(Message.contact))
    
    if contact_id:
        query = query.where(Message.contact_id == contact_id)
    
    if message_type:
        query = query.where(Message.type == message_type)
    
    query = query.order_by(Message.created_at.desc()).limit(limit).offset(offset)
    
    result = await db_session.execute(query)
    return result.scalars().all()


async def delete(*, db_session: AsyncSession, message: Message) -> None:
    """Deletes a message."""
    await db_session.delete(message)
    await db_session.commit()

from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Message


async def get(*, db_session: AsyncSession, contact_id: int, since: datetime = datetime.min) -> Sequence[Message]:
    """Returns the default project."""
    result = await db_session.execute(
        select(Message).where(Message.contact_id == contact_id, Message.created_at > since)
    )
    return result.scalars().all()

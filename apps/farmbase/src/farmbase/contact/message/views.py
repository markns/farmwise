from typing import Annotated, List, Optional

from fastapi import APIRouter, HTTPException, Path, Query
from starlette import status

from farmbase.database.core import DbSession

from . import service
from .models import MessageType
from .schemas import MessageCreate, MessageRead, MessageSummary

router = APIRouter()


@router.get("", response_model=List[MessageSummary])
async def list_messages(
    db_session: DbSession,
    contact_id: Annotated[int, Path(description="Contact ID")],
    message_type: Annotated[Optional[MessageType], Query(description="Filter by message type")] = None,
    limit: Annotated[int, Query(description="Number of messages to return", ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(description="Number of messages to skip", ge=0)] = 0,
):
    """List message summaries for a contact."""
    messages = await service.list_messages(
        db_session=db_session,
        contact_id=contact_id,
        message_type=message_type,
        limit=limit,
        offset=offset,
    )

    summaries = []
    for message in messages:
        # Extract storage URL if available
        storage_url = None
        if message.storage and isinstance(message.storage, dict):
            storage_url = message.storage.get("url")

        match message.type:
            case MessageType.INTERACTIVE:
                text = message.title
            case MessageType.LOCATION:
                text = str(message.location)
            case _:
                text = message.text

        summary = MessageSummary(
            id=message.id,
            timestamp=message.timestamp,
            direction=message.direction,
            type=message.type,
            text=text,
            caption=message.caption,
            storage_url=storage_url,
        )
        summaries.append(summary)

    return summaries


@router.get("/{message_id}", response_model=MessageRead)
async def get_message(
    db_session: DbSession,
    contact_id: Annotated[int, Path(description="Contact ID")],
    message_id: Annotated[int, Path(description="Message ID")],
):
    """Get a specific message."""
    message = await service.get_by_id(db_session=db_session, message_id=message_id)
    if not message or message.contact_id != contact_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    return MessageRead.model_validate(message)


@router.post("", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def create_message(
    db_session: DbSession,
    contact_id: Annotated[int, Path(description="Contact ID")],
    message_in: MessageCreate,
):
    """Create a new message."""
    # Ensure the contact_id in the path matches the one in the payload
    message_in.contact_id = contact_id

    message = await service.create(db_session=db_session, message_in=message_in)
    return MessageRead.model_validate(message)


# @router.patch("/{message_id}", response_model=MessageRead)
# async def update_message(
#     db_session: DbSession,
#     contact_id: Annotated[int, Path(description="Contact ID")],
#     message_id: Annotated[int, Path(description="Message ID")],
#     message_update: MessageUpdate,
# ):
#     """Update a message."""
#     message = await service.get_by_id(db_session=db_session, message_id=message_id)
#     if not message or message.contact_id != contact_id:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Message not found"
#         )
#
#     updated_message = await service.update(
#         db_session=db_session,
#         message=message,
#         message_update=message_update,
#     )
#     return MessageRead.model_validate(updated_message)


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    db_session: DbSession,
    contact_id: Annotated[int, Path(description="Contact ID")],
    message_id: Annotated[int, Path(description="Message ID")],
):
    """Delete a message."""
    message = await service.get_by_id(db_session=db_session, message_id=message_id)
    if not message or message.contact_id != contact_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    await service.delete(db_session=db_session, message=message)


@router.get("/whatsapp/{whatsapp_message_id}", response_model=MessageRead)
async def get_message_by_whatsapp_id(
    db_session: DbSession,
    contact_id: Annotated[int, Path(description="Contact ID")],
    whatsapp_message_id: Annotated[str, Path(description="WhatsApp message ID")],
):
    """Get a message by WhatsApp message ID."""
    message = await service.get_by_whatsapp_id(
        db_session=db_session,
        whatsapp_message_id=whatsapp_message_id,
    )
    if not message or message.contact_id != contact_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    return MessageRead.model_validate(message)

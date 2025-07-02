from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from farmbase.models import FarmbaseBase, PrimaryKey

from .models import MessageDirection, MessageType


class MessageBase(FarmbaseBase):
    contact_id: int = Field(description="ID of the contact")
    direction: MessageDirection = Field(description="Is the message inbound or outbound")
    whatsapp_message_id: str = Field(description="WhatsApp message ID")
    timestamp: datetime = Field(description="When the message was sent")
    type: MessageType = Field(description="Message type")

    # Message flags
    forwarded: bool = Field(default=False, description="Whether the message was forwarded")
    forwarded_many_times: bool = Field(default=False, description="Whether forwarded many times")

    # Content fields
    text: Optional[str] = Field(None, description="Text content")
    caption: Optional[str] = Field(None, description="Media caption")

    # Media and other data as JSON
    image: Optional[dict] = Field(None, description="Image data")
    video: Optional[dict] = Field(None, description="Video data")
    sticker: Optional[dict] = Field(None, description="Sticker data")
    document: Optional[dict] = Field(None, description="Document data")
    audio: Optional[dict] = Field(None, description="Audio data")
    # location of downloaded media
    storage: Optional[dict] = Field(None, description="Location of downloaded media")

    reaction: Optional[dict] = Field(None, description="Reaction data")
    location: Optional[dict] = Field(None, description="Location data")
    contacts: Optional[dict] = Field(None, description="Contacts data")
    order: Optional[dict] = Field(None, description="Order data")
    system: Optional[dict] = Field(None, description="System update data")

    from_user: Optional[dict] = Field(None, description="User who sent the message")
    reply_to_message: Optional[dict] = Field(None, description="Message being replied to")

    # Callback handler info
    data: Optional[str] = Field(None)
    title: Optional[str] = Field(None)
    description: Optional[str] = Field(None)

    # Error handling
    error: Optional[dict] = Field(None, description="Error data if any")


class MessageCreate(MessageBase):
    # Field(alias="metadata_") tells Pydantic: this field maps to metadata_ in the SQLAlchemy model.
    metadata_: Optional[dict[str, Any]] = Field(None, alias="metadata")


class MessageRead(MessageBase):
    id: PrimaryKey = Field(description="Message ID")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    metadata: Optional[dict[str, Any]] = Field(None, alias="metadata_")


class MessageSummary(FarmbaseBase):
    """Simplified message summary for chat display"""

    id: PrimaryKey = Field(description="Message ID")
    timestamp: datetime = Field(description="When the message was sent")
    direction: MessageDirection = Field(description="Is the message inbound or outbound")
    type: MessageType = Field(description="Message type")
    text: Optional[str] = Field(None, description="Text content")
    caption: Optional[str] = Field(None, description="Media caption")
    storage_url: Optional[str] = Field(None, description="URL of downloaded media file")

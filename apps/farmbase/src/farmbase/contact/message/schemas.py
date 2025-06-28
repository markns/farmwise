from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from farmbase.models import FarmbaseBase, PrimaryKey

from .models import MessageType, RecipientType


class MessageBase(FarmbaseBase):
    messaging_product: str = Field(default="whatsapp", description="Messaging product (always 'whatsapp')")
    recipient_type: RecipientType = Field(default=RecipientType.INDIVIDUAL, description="Recipient type")
    to: str = Field(description="Recipient's phone number")
    type: MessageType = Field(default=MessageType.TEXT, description="Message type")
    status: Optional[str] = Field(None, description="Message status")
    biz_opaque_callback_data: Optional[str] = Field(None, max_length=512, description="Business callback data")
    
    audio: Optional[dict] = Field(None, description="Audio message data")
    contacts: Optional[dict] = Field(None, description="Contact message data")
    context: Optional[dict] = Field(None, description="Context for message replies")
    document: Optional[dict] = Field(None, description="Document message data")
    image: Optional[dict] = Field(None, description="Image message data")
    interactive: Optional[dict] = Field(None, description="Interactive message data")
    location: Optional[dict] = Field(None, description="Location message data")
    sticker: Optional[dict] = Field(None, description="Sticker message data")
    template: Optional[dict] = Field(None, description="Template message data")
    text: Optional[dict] = Field(None, description="Text message data")
    reaction: Optional[dict] = Field(None, description="Reaction message data")


class MessageCreate(MessageBase):
    contact_id: int = Field(description="ID of the contact to send message to")


class MessageUpdate(FarmbaseBase):
    status: Optional[str] = Field(None, description="Message status")
    whatsapp_message_id: Optional[str] = Field(None, description="WhatsApp message ID")


class MessageRead(MessageBase):
    id: PrimaryKey = Field(description="Message ID")
    whatsapp_message_id: Optional[str] = Field(None, description="WhatsApp message ID")
    contact_id: int = Field(description="Contact ID")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
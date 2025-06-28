from __future__ import annotations

from enum import Enum
from typing import Optional

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.contact.models import Contact
from farmbase.database.core import Base
from farmbase.models import TimeStampMixin


class MessageType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    DOCUMENT = "document"
    IMAGE = "image"
    INTERACTIVE = "interactive"
    LOCATION = "location"
    STICKER = "sticker"
    TEMPLATE = "template"
    CONTACTS = "contacts"
    REACTION = "reaction"


class RecipientType(str, Enum):
    INDIVIDUAL = "individual"


class Message(Base, TimeStampMixin):
    __tablename__ = "message"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    whatsapp_message_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contact.id"))
    contact: Mapped[Contact] = relationship()
    
    messaging_product: Mapped[str] = mapped_column(String(20), default="whatsapp")
    recipient_type: Mapped[RecipientType] = mapped_column(default=RecipientType.INDIVIDUAL)
    to: Mapped[str] = mapped_column(String(20))
    type: Mapped[MessageType] = mapped_column(default=MessageType.TEXT)
    status: Mapped[Optional[str]] = mapped_column(String(50))
    
    biz_opaque_callback_data: Mapped[Optional[str]] = mapped_column(String(512))
    
    audio: Mapped[Optional[dict]] = mapped_column(JSON)
    contacts: Mapped[Optional[dict]] = mapped_column(JSON)
    context: Mapped[Optional[dict]] = mapped_column(JSON)
    document: Mapped[Optional[dict]] = mapped_column(JSON)
    image: Mapped[Optional[dict]] = mapped_column(JSON)
    interactive: Mapped[Optional[dict]] = mapped_column(JSON)
    location: Mapped[Optional[dict]] = mapped_column(JSON)
    sticker: Mapped[Optional[dict]] = mapped_column(JSON)
    template: Mapped[Optional[dict]] = mapped_column(JSON)
    text: Mapped[Optional[dict]] = mapped_column(JSON)
    reaction: Mapped[Optional[dict]] = mapped_column(JSON)

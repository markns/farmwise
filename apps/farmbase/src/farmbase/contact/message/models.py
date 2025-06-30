from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.contact.models import Contact
from farmbase.database.core import Base
from farmbase.enums import FarmbaseEnum
from farmbase.models import TimeStampMixin


class MessageDirection(FarmbaseEnum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class MessageType(str, Enum):
    # copied from pywa.types.others.MessageType
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"
    STICKER = "sticker"
    REACTION = "reaction"
    LOCATION = "location"
    CONTACTS = "contacts"
    ORDER = "order"
    SYSTEM = "system"
    UNKNOWN = "unknown"
    UNSUPPORTED = "unsupported"

    INTERACTIVE = "interactive"
    BUTTON = "button"
    REQUEST_WELCOME = "request_welcome"


class Message(Base, TimeStampMixin):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contact.id"))
    contact: Mapped[Contact] = relationship()

    direction: Mapped[MessageDirection] = mapped_column(
        SqlEnum(MessageDirection, name="message_direction_enum"), nullable=False
    )

    # Core pywa Message fields
    whatsapp_message_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    type: Mapped[MessageType] = mapped_column()

    # Message flags
    forwarded: Mapped[bool] = mapped_column(Boolean, default=False)
    forwarded_many_times: Mapped[bool] = mapped_column(Boolean, default=False)

    # Content fields
    text: Mapped[Optional[str]] = mapped_column(Text)
    caption: Mapped[Optional[str]] = mapped_column(Text)

    # Media and other data stored as JSON
    image: Mapped[Optional[dict]] = mapped_column(JSON)
    video: Mapped[Optional[dict]] = mapped_column(JSON)
    sticker: Mapped[Optional[dict]] = mapped_column(JSON)
    document: Mapped[Optional[dict]] = mapped_column(JSON)
    audio: Mapped[Optional[dict]] = mapped_column(JSON)
    reaction: Mapped[Optional[dict]] = mapped_column(JSON)
    location: Mapped[Optional[dict]] = mapped_column(JSON)
    contacts: Mapped[Optional[dict]] = mapped_column(JSON)
    order: Mapped[Optional[dict]] = mapped_column(JSON)
    system: Mapped[Optional[dict]] = mapped_column(JSON)
    # location of downloaded media
    storage: Mapped[Optional[dict]] = mapped_column(JSON)

    # Callback handler info
    data: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Metadata and user info
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON)
    from_user: Mapped[Optional[dict]] = mapped_column(JSON)
    reply_to_message: Mapped[Optional[dict]] = mapped_column(JSON)

    # Error handling
    error: Mapped[Optional[dict]] = mapped_column(JSON)

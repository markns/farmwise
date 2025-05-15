from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.contact.models import Contact
from farmbase.database.core import Base
from farmbase.models import TimeStampMixin


class Message(Base, TimeStampMixin):
    __tablename__ = "message"
    id: Mapped[int] = mapped_column(primary_key=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contact.id"))
    contact: Mapped[Contact] = relationship()
    text: Mapped[str] = mapped_column()

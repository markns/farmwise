from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.database.core import Base


class Topic(Base):
    __tablename__ = "topic"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    # Relationship to the Subscription association object
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="topic", cascade="all, delete-orphan")
    # Optional: proxy for direct access to contacts
    subscribers = association_proxy("subscriptions", "contact")

    def __repr__(self):
        return f"<Topic(id={self.id}, name='{self.name}')>"


class Subscription(Base):
    __tablename__ = "subscription"
    contact_id: Mapped[int] = mapped_column(ForeignKey("contact.id"), primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topic.id"), primary_key=True)

    subscribed_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(50), default="active")  # e.g., 'active', 'unsubscribed'

    # Relationships to Contact and Topic
    contact: Mapped["Contact"] = relationship(back_populates="subscriptions")
    topic: Mapped["Topic"] = relationship(back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription(contact_id={self.contact_id}, topic_id={self.topic_id})>"

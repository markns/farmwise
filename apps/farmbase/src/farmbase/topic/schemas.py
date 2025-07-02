from datetime import datetime
from typing import List, Optional

from pydantic import Field

from farmbase.models import FarmbaseBase, Pagination, PrimaryKey


class TopicBase(FarmbaseBase):
    """Base model for Topic data."""

    name: str = Field(description="Name of the topic")
    description: Optional[str] = Field(default=None, description="Description of the topic")


class TopicCreate(TopicBase):
    """Model for creating a new topic."""

    pass


class TopicUpdate(TopicBase):
    """Model for updating an existing topic."""

    name: Optional[str] = Field(default=None, description="Name of the topic")


class TopicRead(TopicBase):
    """Model for reading Topic data."""

    id: PrimaryKey = Field(description="Unique identifier of the topic")


class TopicPagination(Pagination):
    """Model for paginated list of topics."""

    items: List[TopicRead] = Field(default_factory=list, description="List of topics in the current page")


class SubscriptionBase(FarmbaseBase):
    """Base model for Subscription data."""

    subscribed_on: datetime = Field(description="Date and time when the subscription was created")
    status: str = Field(default="active", description="Status of the subscription (active, unsubscribed)")


class SubscriptionCreate(FarmbaseBase):
    """Model for creating a new subscription."""

    contact_id: int = Field(description="ID of the contact")
    topic_id: int = Field(description="ID of the topic")
    status: str = Field(default="active", description="Status of the subscription")


class SubscriptionUpdate(FarmbaseBase):
    """Model for updating an existing subscription."""

    status: Optional[str] = Field(default=None, description="Status of the subscription")


class SubscriptionRead(SubscriptionBase):
    """Model for reading Subscription data."""

    contact_id: int = Field(description="ID of the contact")
    topic_id: int = Field(description="ID of the topic")
    topic: TopicRead = Field(description="Topic information")


class SubscriptionPagination(Pagination):
    """Model for paginated list of subscriptions."""

    items: List[SubscriptionRead] = Field(default_factory=list, description="List of subscriptions in the current page")


class ContactSubscriptionRead(FarmbaseBase):
    """Model for reading a contact's subscription data."""

    contact_id: int = Field(description="ID of the contact")
    subscriptions: List[SubscriptionRead] = Field(description="List of subscriptions for the contact")

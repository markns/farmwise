from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Subscription, Topic
from .schemas import SubscriptionCreate, SubscriptionUpdate, TopicCreate, TopicUpdate


# Topic service functions
async def get_topic(*, db_session: AsyncSession, topic_id: int) -> Optional[Topic]:
    """Returns a topic based on the given topic id."""
    result = await db_session.execute(select(Topic).where(Topic.id == topic_id))
    return result.scalar_one_or_none()


async def get_topic_by_name(*, db_session: AsyncSession, name: str) -> Optional[Topic]:
    """Returns a topic based on the given topic name."""
    result = await db_session.execute(select(Topic).where(Topic.name == name))
    return result.scalar_one_or_none()


async def get_all_topics(*, db_session: AsyncSession, limit: int = 100, offset: int = 0) -> Sequence[Topic]:
    """Returns all topics with pagination."""
    result = await db_session.execute(select(Topic).limit(limit).offset(offset))
    return result.scalars().all()


async def count_topics(*, db_session: AsyncSession) -> int:
    """Returns the total count of topics."""
    from sqlalchemy import func

    result = await db_session.execute(select(func.count(Topic.id)))
    return result.scalar_one()


async def create_topic(*, db_session: AsyncSession, topic_in: TopicCreate) -> Topic:
    """Creates a topic."""
    topic = Topic(**topic_in.model_dump())

    db_session.add(topic)
    await db_session.commit()
    await db_session.refresh(topic)

    return topic


async def update_topic(*, db_session: AsyncSession, topic: Topic, topic_in: TopicUpdate) -> Topic:
    """Updates a topic."""
    update_data = topic_in.model_dump(exclude_unset=True, exclude_none=True)

    for field, value in update_data.items():
        setattr(topic, field, value)

    await db_session.commit()
    await db_session.refresh(topic)
    return topic


async def delete_topic(*, db_session: AsyncSession, topic_id: int) -> None:
    """Deletes a topic."""
    result = await db_session.execute(select(Topic).where(Topic.id == topic_id))
    topic = result.scalar_one_or_none()
    if topic:
        await db_session.delete(topic)
        await db_session.commit()


# Subscription service functions
async def get_subscription(*, db_session: AsyncSession, contact_id: int, topic_id: int) -> Optional[Subscription]:
    """Returns a subscription based on contact_id and topic_id."""
    result = await db_session.execute(
        select(Subscription)
        .options(selectinload(Subscription.topic), selectinload(Subscription.contact))
        .where(Subscription.contact_id == contact_id, Subscription.topic_id == topic_id)
    )
    return result.scalar_one_or_none()


async def get_subscriptions_by_contact(
    *, db_session: AsyncSession, contact_id: int, limit: int = 100, offset: int = 0
) -> Sequence[Subscription]:
    """Returns all subscriptions for a specific contact."""
    result = await db_session.execute(
        select(Subscription)
        .options(selectinload(Subscription.topic))
        .where(Subscription.contact_id == contact_id)
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def get_subscriptions_by_topic(
    *, db_session: AsyncSession, topic_id: int, limit: int = 100, offset: int = 0
) -> Sequence[Subscription]:
    """Returns all subscriptions for a specific topic."""
    result = await db_session.execute(
        select(Subscription)
        .options(selectinload(Subscription.contact))
        .where(Subscription.topic_id == topic_id)
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def get_all_subscriptions(
    *, db_session: AsyncSession, limit: int = 100, offset: int = 0
) -> Sequence[Subscription]:
    """Returns all subscriptions with pagination."""
    result = await db_session.execute(
        select(Subscription)
        .options(selectinload(Subscription.topic), selectinload(Subscription.contact))
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def count_subscriptions(*, db_session: AsyncSession) -> int:
    """Returns the total count of subscriptions."""
    from sqlalchemy import func

    result = await db_session.execute(select(func.count(Subscription.contact_id)))
    return result.scalar_one()


async def create_subscription(*, db_session: AsyncSession, subscription_in: SubscriptionCreate) -> Subscription:
    """Creates a subscription."""
    subscription = Subscription(**subscription_in.model_dump())

    db_session.add(subscription)
    await db_session.commit()
    await db_session.refresh(subscription)

    return await get_subscription(
        db_session=db_session, contact_id=subscription.contact_id, topic_id=subscription.topic_id
    )


async def update_subscription(
    *, db_session: AsyncSession, subscription: Subscription, subscription_in: SubscriptionUpdate
) -> Subscription:
    """Updates a subscription."""
    update_data = subscription_in.model_dump(exclude_unset=True, exclude_none=True)

    for field, value in update_data.items():
        setattr(subscription, field, value)

    await db_session.commit()
    await db_session.refresh(subscription)
    return subscription


async def delete_subscription(*, db_session: AsyncSession, contact_id: int, topic_id: int) -> None:
    """Deletes a subscription."""
    result = await db_session.execute(
        select(Subscription).where(Subscription.contact_id == contact_id, Subscription.topic_id == topic_id)
    )
    subscription = result.scalar_one_or_none()
    if subscription:
        await db_session.delete(subscription)
        await db_session.commit()


async def subscribe_contact_to_topic(*, db_session: AsyncSession, contact_id: int, topic_id: int) -> Subscription:
    """Subscribe a contact to a topic with active status."""
    subscription_data = SubscriptionCreate(contact_id=contact_id, topic_id=topic_id, status="active")
    return await create_subscription(db_session=db_session, subscription_in=subscription_data)


async def unsubscribe_contact_from_topic(*, db_session: AsyncSession, contact_id: int, topic_id: int) -> None:
    """Unsubscribe a contact from a topic by setting status to unsubscribed."""
    subscription = await get_subscription(db_session=db_session, contact_id=contact_id, topic_id=topic_id)
    if subscription:
        subscription_update = SubscriptionUpdate(status="unsubscribed")
        await update_subscription(db_session=db_session, subscription=subscription, subscription_in=subscription_update)

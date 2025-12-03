from typing import Annotated

from fastapi import APIRouter, Path, Query

from farmbase.database.core import DbSession
from farmbase.models import PrimaryKey

from ..exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError
from .schemas import (
    ContactSubscriptionRead,
    SubscriptionCreate,
    SubscriptionPagination,
    SubscriptionRead,
    SubscriptionUpdate,
    TopicCreate,
    TopicPagination,
    TopicRead,
    TopicUpdate,
)
from .service import (
    count_subscriptions,
    count_topics,
    create_subscription,
    create_topic,
    delete_subscription,
    delete_topic,
    get_all_subscriptions,
    get_all_topics,
    get_subscription,
    get_subscriptions_by_contact,
    get_subscriptions_by_topic,
    get_topic,
    get_topic_by_name,
    subscribe_contact_to_topic,
    unsubscribe_contact_from_topic,
    update_subscription,
    update_topic,
)

router = APIRouter()
subscription_router = APIRouter()


# Topic endpoints
@router.get("", response_model=TopicPagination)
async def get_topics(
    db_session: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    items_per_page: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """Get all topics with pagination."""
    offset = (page - 1) * items_per_page
    topics = await get_all_topics(db_session=db_session, limit=items_per_page, offset=offset)
    total = await count_topics(db_session=db_session)

    return TopicPagination(
        items=[TopicRead.model_validate(topic) for topic in topics],
        items_per_page=items_per_page,
        page=page,
        total=total,
    )


@router.post("", response_model=TopicRead)
async def create_topic_endpoint(
    db_session: DbSession,
    topic_in: TopicCreate,
):
    """Create a new topic."""
    existing = await get_topic_by_name(db_session=db_session, name=topic_in.name)
    if existing:
        raise EntityAlreadyExistsError(message="A topic with this name already exists.")

    topic = await create_topic(db_session=db_session, topic_in=topic_in)
    return TopicRead.model_validate(topic)


@router.get("/{topic_id}", response_model=TopicRead)
async def get_topic_endpoint(
    db_session: DbSession,
    topic_id: PrimaryKey,
):
    """Get a specific topic by ID."""
    topic = await get_topic(db_session=db_session, topic_id=topic_id)
    if not topic:
        raise EntityDoesNotExistError(message="Topic not found.")

    return TopicRead.model_validate(topic)


@router.put("/{topic_id}", response_model=TopicRead)
async def update_topic_endpoint(
    db_session: DbSession,
    topic_id: PrimaryKey,
    topic_in: TopicUpdate,
):
    """Update a specific topic."""
    topic = await get_topic(db_session=db_session, topic_id=topic_id)
    if not topic:
        raise EntityDoesNotExistError(message="Topic not found.")

    # Check if name is being updated and ensure it's unique
    if topic_in.name and topic_in.name != topic.name:
        existing = await get_topic_by_name(db_session=db_session, name=topic_in.name)
        if existing:
            raise EntityAlreadyExistsError(message="A topic with this name already exists.")

    updated_topic = await update_topic(db_session=db_session, topic=topic, topic_in=topic_in)
    return TopicRead.model_validate(updated_topic)


@router.delete("/{topic_id}")
async def delete_topic_endpoint(
    db_session: DbSession,
    topic_id: PrimaryKey,
):
    """Delete a specific topic."""
    topic = await get_topic(db_session=db_session, topic_id=topic_id)
    if not topic:
        raise EntityDoesNotExistError(message="Topic not found.")

    await delete_topic(db_session=db_session, topic_id=topic_id)
    return {"message": "Topic deleted successfully"}


# Subscription endpoints
@subscription_router.get("", response_model=SubscriptionPagination)
async def get_subscriptions(
    db_session: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    items_per_page: Annotated[int, Query(ge=1, le=100)] = 50,
    contact_id: int = None,
    topic_id: int = None,
):
    """Get all subscriptions with pagination. Optionally filter by contact_id or topic_id."""
    offset = (page - 1) * items_per_page

    if contact_id:
        subscriptions = await get_subscriptions_by_contact(
            db_session=db_session, contact_id=contact_id, limit=items_per_page, offset=offset
        )
    elif topic_id:
        subscriptions = await get_subscriptions_by_topic(
            db_session=db_session, topic_id=topic_id, limit=items_per_page, offset=offset
        )
    else:
        subscriptions = await get_all_subscriptions(db_session=db_session, limit=items_per_page, offset=offset)

    total = await count_subscriptions(db_session=db_session)

    return SubscriptionPagination(
        items=[SubscriptionRead.model_validate(subscription) for subscription in subscriptions],
        items_per_page=items_per_page,
        page=page,
        total=total,
    )


@subscription_router.post("", response_model=SubscriptionRead)
async def create_subscription_endpoint(
    db_session: DbSession,
    subscription_in: SubscriptionCreate,
):
    """Create a new subscription."""
    existing = await get_subscription(
        db_session=db_session, contact_id=subscription_in.contact_id, topic_id=subscription_in.topic_id
    )
    if existing:
        raise EntityAlreadyExistsError(message="This subscription already exists.")

    subscription = await create_subscription(db_session=db_session, subscription_in=subscription_in)
    return SubscriptionRead.model_validate(subscription)


@subscription_router.get("/{contact_id}/{topic_id}", response_model=SubscriptionRead)
async def get_subscription_endpoint(
    db_session: DbSession,
    contact_id: int,
    topic_id: int,
):
    """Get a specific subscription by contact_id and topic_id."""
    subscription = await get_subscription(db_session=db_session, contact_id=contact_id, topic_id=topic_id)
    if not subscription:
        raise EntityDoesNotExistError(message="Subscription not found.")

    return SubscriptionRead.model_validate(subscription)


@subscription_router.put("/{contact_id}/{topic_id}", response_model=SubscriptionRead)
async def update_subscription_endpoint(
    db_session: DbSession,
    contact_id: int,
    topic_id: int,
    subscription_in: SubscriptionUpdate,
):
    """Update a specific subscription."""
    subscription = await get_subscription(db_session=db_session, contact_id=contact_id, topic_id=topic_id)
    if not subscription:
        raise EntityDoesNotExistError(message="Subscription not found.")

    updated_subscription = await update_subscription(
        db_session=db_session, subscription=subscription, subscription_in=subscription_in
    )
    return SubscriptionRead.model_validate(updated_subscription)


@subscription_router.delete("/{contact_id}/{topic_id}")
async def delete_subscription_endpoint(
    db_session: DbSession,
    contact_id: int,
    topic_id: int,
):
    """Delete a specific subscription."""
    subscription = await get_subscription(db_session=db_session, contact_id=contact_id, topic_id=topic_id)
    if not subscription:
        raise EntityDoesNotExistError(message="Subscription not found.")

    await delete_subscription(db_session=db_session, contact_id=contact_id, topic_id=topic_id)
    return {"message": "Subscription deleted successfully"}


# Convenience endpoints for subscribing/unsubscribing
@subscription_router.post("/subscribe/{contact_id}/{topic_id}", response_model=SubscriptionRead)
async def subscribe_endpoint(
    db_session: DbSession,
    contact_id: int,
    topic_id: int,
):
    """Subscribe a contact to a topic."""
    existing = await get_subscription(db_session=db_session, contact_id=contact_id, topic_id=topic_id)
    if existing and existing.status == "active":
        raise EntityAlreadyExistsError(message="Contact is already subscribed to this topic.")

    subscription = await subscribe_contact_to_topic(db_session=db_session, contact_id=contact_id, topic_id=topic_id)
    return SubscriptionRead.model_validate(subscription)


@subscription_router.post("/unsubscribe/{contact_id}/{topic_id}")
async def unsubscribe_endpoint(
    db_session: DbSession,
    contact_id: int,
    topic_id: int,
):
    """Unsubscribe a contact from a topic."""
    subscription = await get_subscription(db_session=db_session, contact_id=contact_id, topic_id=topic_id)
    if not subscription:
        raise EntityDoesNotExistError(message="Subscription not found.")

    await unsubscribe_contact_from_topic(db_session=db_session, contact_id=contact_id, topic_id=topic_id)
    return {"message": "Successfully unsubscribed from topic"}


# Contact subscription endpoints
@subscription_router.get("/contact/{contact_id}", response_model=ContactSubscriptionRead)
async def get_contact_subscriptions(
    db_session: DbSession,
    contact_id: Annotated[int, Path(description="Contact ID")],
    page: Annotated[int, Query(ge=1)] = 1,
    items_per_page: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """Get all subscriptions for a specific contact."""
    offset = (page - 1) * items_per_page
    subscriptions = await get_subscriptions_by_contact(
        db_session=db_session, contact_id=contact_id, limit=items_per_page, offset=offset
    )

    return ContactSubscriptionRead(
        contact_id=contact_id,
        subscriptions=[SubscriptionRead.model_validate(subscription) for subscription in subscriptions],
    )

from datetime import datetime
from typing import Annotated

from farmbase_client import AuthenticatedClient
from farmbase_client.api.contacts import contacts_get_or_create_contact
from farmbase_client.models import ContactCreate
from farmwise_schema.schema import UserInput
from fastapi import Depends
from loguru import logger
from openai.types.responses import EasyInputMessageParam
from pydantic import BaseModel
from sqlmodel import Session, select

from farmwise.context import UserContext
from farmwise.database import Message, get_session
from farmwise.settings import settings


def chat_history(user_input: UserInput, session: Session = Depends(get_session)):
    statement = (
        select(Message.role, Message.content).where(Message.user_id == user_input.user_id).order_by(Message.id.desc())
    )
    results = [
        EasyInputMessageParam(role=row.role, content=row.content) for row in reversed(session.exec(statement).all())
    ]
    return results


class ChatState(BaseModel):
    current_agent: str | None = None
    previous_response_id: str | None = None
    timestamp: datetime | None = None
    trace_id: str | None = None


def chat_state(user_input: UserInput, session: Session = Depends(get_session)):
    statement = (
        select(Message.agent, Message.previous_response_id)
        .where(Message.user_id == user_input.user_id)
        .order_by(Message.id.desc())
        .limit(1)
    )

    results = session.exec(statement).one_or_none()
    if results:
        return ChatState(
            current_agent=results.agent,
            previous_response_id=results.previous_response_id,
            timestamp=None,
            trace_id=None,
        )

    return ChatState()


ChatStateDep = Annotated[ChatState, Depends(chat_state)]


# TODO: how does organization get set?
async def user_context(user_input: UserInput, organization="default"):
    with AuthenticatedClient(base_url=settings.FARMBASE_ENDPOINT, token=settings.FARMBASE_API_KEY) as client:
        result = await contacts_get_or_create_contact.asyncio(
            client=client,
            organization=organization,
            body=ContactCreate(name=user_input.user_name, phone_number=user_input.user_id),
        )
        context = UserContext(
            user_id=result.id,
            name=result.name,
            location=result.location,
            phone_number=result.phone_number,
            organization=organization,
        )
        logger.debug(f"loaded context {context}")
        return context

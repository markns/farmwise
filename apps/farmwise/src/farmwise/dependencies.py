from farmbase_client import AuthenticatedClient
from farmbase_client.api.contacts import contacts_get_or_create_contact
from farmbase_client.models import ContactCreate
from farmwise_schema.schema import UserInput
from fastapi import Depends
from loguru import logger
from openai.types.responses import EasyInputMessageParam
from sqlmodel import Session, select

from farmwise.agents import DEFAULT_AGENT, agents
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


def current_agent(user_input: UserInput, session: Session = Depends(get_session)):
    statement = select(Message.agent).where(Message.user_id == user_input.user_id).order_by(Message.id.desc()).limit(1)

    try:
        return agents[session.exec(statement).one_or_none()]
    except KeyError:
        return agents[DEFAULT_AGENT]


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

from typing import Annotated

from farmbase_client import AuthenticatedClient
from farmbase_client.api.contacts import contacts_get_or_create_contact
from farmbase_client.api.messages import messages_get_chat_state
from farmbase_client.models import ChatState, ContactCreate
from farmwise_schema.schema import UserInput
from fastapi import Depends
from loguru import logger

from farmwise.context import UserContext
from farmwise.settings import settings


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


UserContextDep = Annotated[UserContext, Depends(user_context)]


# TODO: Dependency caching can be used to get all state
async def chat_state(context: UserContextDep) -> ChatState:
    with AuthenticatedClient(base_url="http://127.0.0.1:8000/api/v1", token="fdsfds") as client:
        return await messages_get_chat_state.asyncio(
            organization=context.organization, client=client, contact_id=context.user_id
        )


ChatStateDep = Annotated[ChatState, Depends(chat_state)]

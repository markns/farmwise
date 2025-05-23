from typing import Annotated

from farmbase_client import AuthenticatedClient
from farmbase_client.api.chatstate import chatstate_get_chat_state as get_chat_state
from farmbase_client.api.contacts import contacts_create_contact as create_contact
from farmbase_client.api.contacts import contacts_get_contact_by_phone as get_contact_by_phone
from farmbase_client.models import ChatState, ContactCreate, ContactRead
from farmwise_schema.schema import UserInput
from fastapi import Depends
from pydantic import BaseModel

from farmwise.settings import settings


class UserContext(BaseModel):
    contact: ContactRead
    new_user: bool = False


# TODO: how does organization get set?
async def user_context(user_input: UserInput, organization="default"):
    with AuthenticatedClient(base_url=settings.FARMBASE_ENDPOINT, token=settings.FARMBASE_API_KEY) as client:
        contact = await get_contact_by_phone.asyncio(
            client=client,
            organization=organization,
            phone=user_input.user_id,
        )
        if contact:
            context = UserContext(
                contact=contact,
            )
        else:
            contact = await create_contact.asyncio(
                client=client,
                organization=organization,
                body=ContactCreate(
                    name=user_input.user_name,
                    phone_number=user_input.user_id,
                ),
            )
            context = UserContext(contact=contact, new_user=True)

        return context


UserContextDep = Annotated[UserContext, Depends(user_context)]


# TODO: Dependency caching can be used to get all state
async def chat_state(context: UserContextDep) -> ChatState:
    with AuthenticatedClient(base_url=settings.FARMBASE_ENDPOINT, token=settings.FARMBASE_API_KEY) as client:
        return await get_chat_state.asyncio(
            organization=context.contact.organization.slug,
            client=client,
            contact_id=context.contact.id,
        )


ChatStateDep = Annotated[ChatState, Depends(chat_state)]

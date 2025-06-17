from typing import Annotated

from farmbase_client.api.chatstate import chatstate_get_chat_state as get_chat_state
from farmbase_client.api.contacts import contacts_create_contact as create_contact
from farmbase_client.api.contacts import contacts_get_contact_by_phone as get_contact_by_phone
from farmbase_client.models import ChatState, ContactCreate, ContactRead
from fastapi import Depends
from loguru import logger
from pydantic import BaseModel, ValidationError

from farmwise.farmbase import FarmbaseClient
from farmwise.schema import UserInput


class UserContext(BaseModel):
    contact: ContactRead
    new_user: bool = False


# TODO: how does organization get set?
async def user_context(user_input: UserInput, organization="default"):
    async with FarmbaseClient() as client:
        # TODO: Handle errors better, more consistently in farmbase.
        try:
            contact = await get_contact_by_phone.asyncio(
                client=client.raw,
                organization=organization,
                phone=user_input.user_id,
            )

            context = UserContext(
                contact=contact,
            )
        except ValidationError as e:
            logger.warning(f"User not found: {e}")

            contact = await create_contact.asyncio(
                client=client.raw,
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
    async with FarmbaseClient() as client:
        return await get_chat_state.asyncio(
            organization=context.contact.organization.slug,
            client=client.raw,
            contact_id=context.contact.id,
        )


ChatStateDep = Annotated[ChatState, Depends(chat_state)]

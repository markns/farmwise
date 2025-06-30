from farmbase_client.api.contacts import contacts_create_contact as create_contact
from farmbase_client.api.contacts import contacts_get_all_memories
from farmbase_client.api.contacts import contacts_get_contact_by_phone as get_contact_by_phone
from farmbase_client.models import ContactCreate, ContactRead, MemoryItem
from loguru import logger
from pydantic import BaseModel

from farmwise.farmbase import FarmbaseClient


class UserContext(BaseModel):
    contact: ContactRead
    new_user: bool = False
    memories: list[MemoryItem] = []


# TODO: how does organization get set -
#  maybe an endpoint that searches all schemas?
async def user_context(wa_id: str, name: str, organization="default") -> UserContext:
    async with FarmbaseClient() as client:
        # TODO: Handle errors better, more consistently in farmbase.
        #  - in particular, look at client. raise_on_unexpected_status
        #  and https://fastapi.tiangolo.com/tutorial/handling-errors/#requestvalidationerror-vs-validationerror
        try:
            contact = await get_contact_by_phone.asyncio(
                client=client.raw,
                organization=organization,
                phone=wa_id,
            )
            memories = await contacts_get_all_memories.asyncio(
                organization=contact.organization.slug,
                contact_id=contact.id,
                client=client.raw
            )

            return UserContext(
                contact=contact,
                memories=memories.results
            )
        except Exception as e:
            logger.warning(f"User not found: {e}")

            contact = await create_contact.asyncio(
                client=client.raw,
                organization=organization,
                body=ContactCreate(
                    name=name,
                    phone_number=wa_id,
                ),
            )

            return UserContext(contact=contact, new_user=True)

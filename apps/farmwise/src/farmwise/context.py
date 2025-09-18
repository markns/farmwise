import phonenumbers
from farmbase_client.api.contacts import contacts_create_contact as create_contact
from farmbase_client.models import ContactCreate, ContactRead, MemoryItem
from loguru import logger
from pydantic import BaseModel

from farmwise.farmbase import farmbase_api_client
from farmwise.farmbetter.users import User, get_user


class UserContext(BaseModel):
    contact: ContactRead
    user: User
    new_user: bool = False
    memories: list[MemoryItem] = []


async def user_context(wa_id: str, name: str, organization="default") -> UserContext:
    # TODO: how to update my phone number?
    if wa_id == "31657775781":
        wa_id = "254712345676"

    try:
        number = phonenumbers.parse(wa_id)
        user = get_user(number.country_code, number.national_number)
        # contact = await get_contact_by_phone.asyncio(
        # memories = await contacts_get_all_memories.asyncio(
        #     organization=contact.organization.slug, contact_id=contact.id, client=farmbase_api_client
        # )

        return UserContext(user=user, memories=[])
    except Exception as e:
        logger.warning(f"User not found: {e}")

        contact = await create_contact.asyncio(
            client=farmbase_api_client,
            organization=organization,
            body=ContactCreate(
                name=name,
                phone_number=wa_id,
            ),
        )

        return UserContext(contact=contact, new_user=True)

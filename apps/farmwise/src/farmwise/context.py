import phonenumbers
from loguru import logger
from pydantic import BaseModel

from farmwise.farmbetter.users import User, get_user


class UserContext(BaseModel):
    user: User
    new_user: bool = False
    memories: str | None = None


async def get_or_create_user(wa_id: str, name: str, organization="default") -> UserContext:
    # TODO: how to update my phone number?
    if wa_id == "31657775781":
        wa_id = "254712345676"
        # wa_id = "254111269800"

    try:
        number = phonenumbers.parse(f"+{wa_id}")
        user = await get_user(number.country_code, number.national_number)
        return UserContext(user=user)
    except Exception as e:
        logger.warning(f"User with wa_id {wa_id} name {name} not found: ({type(e)}) {e}")
        raise
        # TODO: Create user in farmbetter?
        # user = await create_contact.asyncio(
        #     client=farmbase_api_client,
        #     organization=organization,
        #     body=ContactCreate(
        #         name=name,
        #         phone_number=wa_id,
        #     ),
        # )

        # return UserContext(user=user, new_user=True)

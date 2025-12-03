import phonenumbers
from loguru import logger
from pydantic import BaseModel

from assistant.farmbetter.models import (
    FieldGqUserModel,
    GqTenantInput,
    GqUserLocationInput,
    GqUserModelDto,
)
from assistant.farmbetter.users import FarmBetterAPIError, create_user, get_user_by_phone
from assistant.settings import settings


class UserContext(BaseModel):
    user: GqUserModelDto
    new_user: bool = False


async def get_or_create_user(wa_id: str) -> UserContext:
    number = phonenumbers.parse(f"+{wa_id}")
    try:
        user = await get_user_by_phone(country_code=number.country_code, national_number=number.national_number)
        logger.info(f"loaded user {user}")
        return UserContext(user=user)
    except FarmBetterAPIError as e:
        logger.warning(f"User with wa_id {wa_id} not found: ({type(e)}) {e}")

        user = await create_user(
            FieldGqUserModel(
                countryCode=str(number.country_code),
                phoneNumber=str(number.national_number),
                firstName="unknown",
                lastName="unknown",
                tenants=[GqTenantInput(id=settings.FARMBETTER_DEFAULT_TENANT, isPrivate=False)],
                location=GqUserLocationInput(lat=0, lng=0, name="Unknown"),
                gender="other",
                type="farmer",
                signUpMode="whatsapp",
            )
        )
        return UserContext(user=user, new_user=True)

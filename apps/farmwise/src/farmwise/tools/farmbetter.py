from agents import RunContextWrapper, function_tool

from farmwise.context import UserContext
from farmwise.farmbetter.models import (
    FieldGqUserModel,
    GqUserModelDto,
    OmittedUpdateUserRequest,
)
from farmwise.farmbetter.users import create_user, get_user_by_phone, update_user


@function_tool(
    description_override="""
Fetch a FarmBetter user by id, email, or phone number. Defaults to the current user in context when no lookup parameters are supplied.
"""
)
async def get_farmbetter_user(
    wrapper: RunContextWrapper[UserContext],
    user_id: str | None = None,
    email: str | None = None,
    country_code: int | None = None,
    national_number: int | None = None,
) -> GqUserModelDto:
    if (
        user_id is None
        and email is None
        and (country_code is None or national_number is None)
        and wrapper.context.user is not None
    ):
        return wrapper.context.user

    user = await get_user_by_phone(
        user_id=user_id,
        email=email,
        country_code=country_code,
        national_number=national_number,
    )
    wrapper.context.user = user
    wrapper.context.new_user = False
    return user


@function_tool(
    description_override="""
Create a new FarmBetter user. Provide the details required by the FarmBetter API in the user payload.
"""
)
async def create_farmbetter_user(wrapper: RunContextWrapper[UserContext], user: FieldGqUserModel) -> GqUserModelDto:
    created_user = await create_user(user=user)
    wrapper.context.user = created_user
    wrapper.context.new_user = True
    return created_user


@function_tool(
    description_override="""
Update an existing FarmBetter user. If the payload omits an id, the current user from context will be used.
"""
)
async def update_farmbetter_user(
    wrapper: RunContextWrapper[UserContext], user: OmittedUpdateUserRequest
) -> GqUserModelDto:
    if user.id is None and wrapper.context.user is not None and wrapper.context.user.id is not None:
        user = user.model_copy(update={"id": wrapper.context.user.id})

    updated_user = await update_user(user=user)
    wrapper.context.user = updated_user
    wrapper.context.new_user = False
    return updated_user

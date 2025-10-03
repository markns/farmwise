from gql import gql

from farmwise.farmbetter import FarmBetterAPIError, farmbetter_client
from farmwise.farmbetter.models import (
    FieldGqUserModel,
    GqUserModelDto,
    OmittedUpdateUserRequest,
)
from farmwise.farmbetter.utils import strip_typename


async def get_user_by_phone(
    country_code: int | None = None,
    national_number: int | None = None,
) -> GqUserModelDto:
    query = gql(
        """
        query GetUser($phoneNumber: GqPhoneNumberUserRequest) {
            getUser(phoneNumber: $phoneNumber) {
                message
                status
                payload {
                    id
                    firstName
                    lastName
                    phoneNumber
                    countryCode
                    countryIso
                    email
                    preferredLanguage
                    status
                    type
                    created
                    updated
                    crops {
                        id
                        name
                    }
                    livestock {
                        id
                        name
                    }
                    fcmNotificationTokens
                    tenantIds
                    dateOfBirth
                    gender
                    maritalStatus
                    education
                    occupation
                    location {
                        lat
                        lng
                        name
                    }
                }
            }
        }
        """
    )

    variables = {
        "phoneNumber": {
            "countryCode": str(country_code),
            "phone": str(national_number),
        }
    }

    async with farmbetter_client as session:
        result = await session.execute(query, variable_values=variables)

    response = result["getUser"]
    if response["status"] != 200:
        raise FarmBetterAPIError(response.get("message", "Unknown error"))

    return GqUserModelDto(**response["payload"])


async def create_user(user: FieldGqUserModel) -> GqUserModelDto:
    mutation = gql(
        """
        mutation CreateUser($user: _GqUserModel!) {
            createUser(user: $user) {
                message
                status
                payload {
                    id
                    firstName
                    lastName
                    phoneNumber
                    countryCode
                    countryIso
                    email
                    preferredLanguage
                    status
                    type
                    created
                    updated
                    crops {
                        id
                        name
                    }
                    livestock {
                        id
                        name
                    }
                    fcmNotificationTokens
                    tenantIds
                    dateOfBirth
                    gender
                    maritalStatus
                    education
                    occupation
                    location {
                        lat
                        lng
                        name
                    }
                }
            }
        }
        """
    )

    async with farmbetter_client as session:
        result = await session.execute(
            mutation, variable_values={"user": strip_typename(user.model_dump(exclude_none=True))}
        )

    response = result["createUser"]
    if response["status"] != 200:
        raise FarmBetterAPIError(response.get("message", "Unknown error"))

    return GqUserModelDto(**response["payload"])


async def update_user(user: OmittedUpdateUserRequest) -> GqUserModelDto:
    mutation = gql(
        """
        mutation UpdateUser($user: OmittedUpdateUserRequest!) {
            updateUser(user: $user) {
                message
                status
                payload {
                    id
                    firstName
                    lastName
                    phoneNumber
                    countryCode
                    countryIso
                    email
                    preferredLanguage
                    status
                    type
                    created
                    updated
                    crops {
                        id
                        name
                    }
                    livestock {
                        id
                        name
                    }
                    fcmNotificationTokens
                    tenantIds
                    dateOfBirth
                    gender
                    maritalStatus
                    education
                    occupation
                    location {
                        lat
                        lng
                        name
                    }
                }
            }
        }
        """
    )

    async with farmbetter_client as session:
        result = await session.execute(
            mutation, variable_values={"user": strip_typename(user.model_dump(exclude_none=True))}
        )

    response = result["updateUser"]
    if response["status"] != 200:
        raise FarmBetterAPIError(response.get("message", "Unknown error"))

    return GqUserModelDto(**response["payload"])

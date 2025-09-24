from gql import gql

from farmwise.farmbetter import farmbetter_client
from farmwise.farmbetter.models import (
    FieldGqUserModel,
    GqUserModelDto,
    OmittedUpdateUserRequest,
)


class FarmBetterAPIError(Exception):
    pass


def _strip_typename(data):
    if isinstance(data, dict):
        return {k: _strip_typename(v) for k, v in data.items() if k != "typename__"}
    elif isinstance(data, list):
        return [_strip_typename(v) for v in data]
    return data


async def get_user(
    user_id: str | None = None,
    email: str | None = None,
    country_code: int | None = None,
    national_number: int | None = None,
) -> GqUserModelDto:
    query = gql(
        """
        query GetUser($id: String, $email: String, $phoneNumber: GqPhoneNumberUserRequest) {
            getUser(id: $id, email: $email, phoneNumber: $phoneNumber) {
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

    variables: dict = {"id": user_id, "email": email}
    if country_code and national_number:
        variables["phoneNumber"] = {
            "countryCode": str(country_code),
            "phone": str(national_number),
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
            mutation, variable_values={"user": _strip_typename(user.model_dump(exclude_none=True))}
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
            mutation, variable_values={"user": _strip_typename(user.model_dump(exclude_none=True))}
        )

    response = result["updateUser"]
    if response["status"] != 200:
        raise FarmBetterAPIError(response.get("message", "Unknown error"))

    return GqUserModelDto(**response["payload"])

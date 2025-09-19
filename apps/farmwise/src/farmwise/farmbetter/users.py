from typing import List, Optional

from gql import gql
from pydantic import BaseModel, computed_field

from farmwise.farmbetter import farmbetter_client


def to_snake(string: str) -> str:
    """Convert GraphQL camelCase fields to snake_case for Python attributes."""
    import re

    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()


# add next to your to_snake (you can keep to_snake if you use it elsewhere)
def to_camel(s: str) -> str:
    """Convert snake_case field names to camelCase aliases used by GraphQL."""
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:]) if parts else s


class BaseGraphQLModel(BaseModel):
    model_config = {
        "alias_generator": to_camel,  # generate aliases like getUser, firstName, ...
        "populate_by_name": True,  # allow either alias or field name
    }


class Livestock(BaseGraphQLModel):
    name: str


class Crop(BaseGraphQLModel):
    name: str


class Specialization(BaseGraphQLModel):
    name: str


class Location(BaseGraphQLModel):
    lat: float
    lng: float


class ExtensionAgent(BaseGraphQLModel):
    first_name: str
    last_name: str
    id: str


class User(BaseGraphQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country_code: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    type: Optional[str] = None
    date_of_birth: Optional[str] = None  # could be datetime if API returns ISO
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    preferred_language: Optional[str] = None
    livestock: Optional[List[Livestock]] = None
    crops: Optional[List[Crop]] = None
    specialization: Optional[List[Specialization]] = None
    location: Optional[Location] = None
    assigned_extension_agent_model: Optional[ExtensionAgent] = None

    # (Optional) be explicit about eq/hash semantics
    def __hash__(self) -> int:
        return hash(self.wa_id)

    def __eq__(self, other) -> bool:
        return isinstance(other, User) and self.wa_id == other.wa_id

    @computed_field(return_type=Optional[str])
    def full_name(self) -> Optional[str]:
        return f"{self.first_name} {self.last_name}"

    @computed_field(return_type=Optional[str])
    def wa_id(self) -> Optional[str]:
        """WhatsApp ID: E.164 numeric without '+' = country_code + national number."""
        return f"{self.country_code}{self.phone_number}"


class GetUserResponse(BaseGraphQLModel):
    message: str
    status: int
    payload: Optional[User] = None


class GetUserData(BaseGraphQLModel):
    get_user: GetUserResponse


async def get_user(country_code: int, national_number: int):
    async with farmbetter_client as session:
        query = gql("""
            query GetUser($phoneNumber: GqPhoneNumberUserRequest) {
              getUser(phoneNumber: $phoneNumber) {
                message
                status
                payload {
                  firstName
                  lastName
                  type
                  countryCode
                  phoneNumber
                  email
                  dateOfBirth
                  gender
                  maritalStatus
                  preferredLanguage
                  livestock {
                    name
                  }
                  crops {
                    name
                  }
                  specialization {
                    name
                  }      
                  location {
                    lat
                    lng
                  }
                  assignedExtensionAgentModel {
                    firstName
                    lastName
                    id
                  }
                }
              }
            }
        """)
        result = await session.execute(
            query, variable_values={"phoneNumber": {"countryCode": str(country_code), "phone": str(national_number)}}
        )
        parsed = GetUserData.model_validate(result)

        return parsed.get_user.payload

# You can use the context for things like:
#
# - Contextual data for your run (e.g. things like a username/uid or other information about the user)
# - Dependencies (e.g. logger objects, data fetchers, etc)
# - Helper functions
from farmbase_client.models import Location
from pydantic import BaseModel

#
# class UserContext(BaseModel):
#     name: str | None = None
#     user_id: str | None = None
#     passenger_name: str | None = None
#     confirmation_number: str | None = None
#     seat_number: str | None = None
#     flight_number: str | None = None


class UserContext(BaseModel):
    user_id: int
    name: str = ""
    phone_number: str = ""
    organization: str = "default"
    location: Location
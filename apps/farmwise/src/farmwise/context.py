from typing import Annotated

from fastapi import Depends

# You can use the context for things like:
#
# - Contextual data for your run (e.g. things like a username/uid or other information about the user)
# - Dependencies (e.g. logger objects, data fetchers, etc)
# - Helper functions

#
# class UserContext(BaseModel):
#     name: str | None = None
#     user_id: str | None = None
#     passenger_name: str | None = None
#     confirmation_number: str | None = None
#     seat_number: str | None = None
#     flight_number: str | None = None


class UserContext:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


UserContextDep = Annotated[UserContext, Depends()]

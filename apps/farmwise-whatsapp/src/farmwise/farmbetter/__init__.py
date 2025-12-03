from gql import Client
from gql.transport.httpx import HTTPXAsyncTransport

from farmwise.settings import settings


class FarmBetterAPIError(Exception):
    """Raised when the FarmBetter API responds with a non-success status."""


TIMEOUT = 20

transport = HTTPXAsyncTransport(
    url=settings.FARMBETTER_ENDPOINT,
    headers={"Authorization": f"Bearer {settings.FARMBETTER_TOKEN.get_secret_value()}"},
    timeout=TIMEOUT,
)

# Create a GraphQL client using the defined transport
farmbetter_client = Client(transport=transport, fetch_schema_from_transport=True, execute_timeout=TIMEOUT)

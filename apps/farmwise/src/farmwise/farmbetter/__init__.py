from gql import Client
from gql.transport.httpx import HTTPXAsyncTransport

from farmwise.settings import settings

transport = HTTPXAsyncTransport(
    url=settings.FARMBETTER_ENDPOINT,
    headers={"Authorization": f"Bearer {settings.FARMBETTER_TOKEN.get_secret_value()}"},
)

# Create a GraphQL client using the defined transport
farmbetter_client = Client(transport=transport, fetch_schema_from_transport=True)

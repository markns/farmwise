from farmbase_client import AuthenticatedClient

from farmwise.settings import settings

# Module-level client instance - connection pool persists across requests
farmbase_api_client = AuthenticatedClient(
    base_url=settings.FARMBASE_ENDPOINT,
    token=settings.FARMBASE_API_KEY.get_secret_value(),
    prefix="",
    auth_header_name="X-Farmbase-Key",
    raise_on_unexpected_status=True,
)

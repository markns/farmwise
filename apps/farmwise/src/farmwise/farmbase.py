from farmbase_client import AuthenticatedClient

# Module-level client instance - connection pool persists across requests
farmbase_api_client = AuthenticatedClient(
    base_url="DEPRECATED",  # settings.FARMBASE_ENDPOINT,
    token="DEPRECATED",  # settings.FARMBASE_API_KEY.get_secret_value(),
    prefix="",
    auth_header_name="X-Farmbase-Key",
    raise_on_unexpected_status=True,
)

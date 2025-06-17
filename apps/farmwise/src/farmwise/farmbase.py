from farmbase_client import AuthenticatedClient

from farmwise.settings import settings


class FarmbaseClient:
    def __init__(self, organization: str = "default"):
        self.organization = organization
        self._client_cm = None
        self.client: AuthenticatedClient | None = None

    async def __aenter__(self):
        self._client_cm = AuthenticatedClient(
            base_url=settings.FARMBASE_ENDPOINT,
            token=settings.FARMBASE_API_KEY.get_secret_value(),
            prefix="",
            auth_header_name="X-Farmbase-Key",
        )
        self.client = await self._client_cm.__aenter__()  # NOTE: important
        return self

    async def __aexit__(self, *args, **kwargs):
        if self._client_cm:
            await self._client_cm.__aexit__(*args, **kwargs)

    @property
    def raw(self) -> AuthenticatedClient:
        assert self.client is not None, "Client not initialized"
        return self.client

from starlette.requests import Request

from farmbase.plugins.base import Plugin


class AuthenticationProviderPlugin(Plugin):
    type = "auth-provider"

    def get_current_user(self, request: Request, **kwargs):
        raise NotImplementedError

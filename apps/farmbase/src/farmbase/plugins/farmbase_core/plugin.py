"""
.. module: farmbase.plugins.farmbase_core.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""

import base64
import json
import logging

import requests
from fastapi import HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from jose.exceptions import JWKError
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from farmbase.config import (
    FARMBASE_AUTHENTICATION_PROVIDER_HEADER_NAME,
    FARMBASE_AUTHENTICATION_PROVIDER_PKCE_JWKS,
    FARMBASE_JWT_AUDIENCE,
    FARMBASE_JWT_EMAIL_OVERRIDE,
    FARMBASE_JWT_SECRET,
    FARMBASE_PKCE_DONT_VERIFY_AT_HASH,
)
from farmbase.plugins import farmbase_core as farmbase_plugin
from farmbase.plugins.bases import AuthenticationProviderPlugin

log = logging.getLogger(__name__)


class BasicAuthProviderPlugin(AuthenticationProviderPlugin):
    title = "Farmbase Plugin - Basic Authentication Provider"
    slug = "farmbase-auth-provider-basic"
    description = "Generic basic authentication provider."
    version = farmbase_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/farmbase.git"

    def get_current_user(self, request: Request, **kwargs):
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            log.exception(
                f"Malformed authorization header. Scheme: {scheme} Param: {param} Authorization: {authorization}"
            )
            return

        token = authorization.split()[1]

        try:
            data = jwt.decode(token, FARMBASE_JWT_SECRET)
        except (JWKError, JWTError):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=[{"msg": "Could not validate credentials"}],
            ) from None
        return data["email"]


class PKCEAuthProviderPlugin(AuthenticationProviderPlugin):
    title = "Farmbase Plugin - PKCE Authentication Provider"
    slug = "farmbase-auth-provider-pkce"
    description = "Generic PCKE authentication provider."
    version = farmbase_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/farmbase.git"

    def get_current_user(self, request: Request, **kwargs):
        credentials_exception = HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=[{"msg": "Could not validate credentials"}]
        )

        authorization: str = request.headers.get("Authorization", request.headers.get("authorization"))
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise credentials_exception

        token = authorization.split()[1]

        # Parse out the Key information. Add padding just in case
        key_info = json.loads(base64.b64decode(token.split(".")[0] + "=========").decode("utf-8"))

        # Grab all possible keys to account for key rotation and find the right key
        keys = requests.get(FARMBASE_AUTHENTICATION_PROVIDER_PKCE_JWKS).json()["keys"]
        for potential_key in keys:
            if potential_key["kid"] == key_info["kid"]:
                key = potential_key

        try:
            jwt_opts = {}
            if FARMBASE_PKCE_DONT_VERIFY_AT_HASH:
                jwt_opts = {"verify_at_hash": False}
            # If FARMBASE_JWT_AUDIENCE is defined, the we must include audience in the decode
            if FARMBASE_JWT_AUDIENCE:
                data = jwt.decode(token, key, audience=FARMBASE_JWT_AUDIENCE, options=jwt_opts)
            else:
                data = jwt.decode(token, key, options=jwt_opts)
        except JWTError as err:
            log.debug("JWT Decode error: {}".format(err))
            raise credentials_exception from err

        # Support overriding where email is returned in the id token
        if FARMBASE_JWT_EMAIL_OVERRIDE:
            return data[FARMBASE_JWT_EMAIL_OVERRIDE]
        else:
            return data["email"]


class HeaderAuthProviderPlugin(AuthenticationProviderPlugin):
    title = "Farmbase Plugin - HTTP Header Authentication Provider"
    slug = "farmbase-auth-provider-header"
    description = "Authenticate users based on HTTP request header."
    version = farmbase_plugin.__version__

    author = "Filippo Giunchedi"
    author_url = "https://github.com/filippog"

    def get_current_user(self, request: Request, **kwargs):
        value: str = request.headers.get(FARMBASE_AUTHENTICATION_PROVIDER_HEADER_NAME)
        if not value:
            log.error(f"Unable to authenticate. Header {FARMBASE_AUTHENTICATION_PROVIDER_HEADER_NAME} not found.")
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
        return value

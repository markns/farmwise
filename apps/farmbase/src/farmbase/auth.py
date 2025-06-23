from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from loguru import logger
from propelauth_fastapi import init_auth
from starlette.status import HTTP_401_UNAUTHORIZED

from farmbase.config import settings

logger.debug("initialising auth")
auth = init_auth(
    "https://6366051.propelauthtest.com",
    "55d4e0fdd0fc9dd65350587b34d5a25982781c1e7eea7b826469337db8f912140473230a1b5a3c6ca37acb21d0ef25fb",
    debug_mode=True,
    log_exceptions=True,
)
logger.debug("finished initialising auth")

# API Key - For machine auth
api_key_scheme = APIKeyHeader(name="X-Farmbase-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_scheme)):
    if api_key == settings.FARMBASE_API_KEY.get_secret_value():
        return {"machine": "trusted_client"}
    return None


# Composite dependency: Accept either
def authenticate_user_or_machine(
    api_key_result=Depends(verify_api_key),
    user=Depends(auth.optional_user),
):
    if user:
        return user
    if api_key_result:
        return api_key_result
    raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated")

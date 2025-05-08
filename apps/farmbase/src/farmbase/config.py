import os
from typing import List
from urllib import parse

from pydantic import BaseModel
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret


class BaseConfigurationModel(BaseModel):
    pass


def get_env_tags(tag_list: List[str]) -> dict:
    """Create dictionary of available env tags."""
    tags = {}
    for t in tag_list:
        tag_key, env_key = t.split(":")

        env_value = os.environ.get(env_key)

        if env_value:
            tags.update({tag_key: env_value})

    return tags


config = Config(".env")


# LOG_LEVEL = config("LOG_LEVEL", default=logging.WARNING)
ENV = config("ENV", default="local")

ENV_TAG_LIST = config("ENV_TAGS", cast=CommaSeparatedStrings, default="")
ENV_TAGS = get_env_tags(ENV_TAG_LIST)

FARMBASE_UI_URL = config("FARMBASE_UI_URL", default="http://localhost:8080")
FARMBASE_ENCRYPTION_KEY = config("FARMBASE_ENCRYPTION_KEY", cast=Secret)


# authentication
VITE_FARMBASE_AUTH_REGISTRATION_ENABLED = config("VITE_FARMBASE_AUTH_REGISTRATION_ENABLED", default="true")
FARMBASE_AUTH_REGISTRATION_ENABLED = VITE_FARMBASE_AUTH_REGISTRATION_ENABLED != "false"

FARMBASE_AUTHENTICATION_PROVIDER_SLUG = config(
    "FARMBASE_AUTHENTICATION_PROVIDER_SLUG",
    default="",
    # default="farmbase-auth-provider-basic"
)

FARMBASE_JWT_AUDIENCE = config("FARMBASE_JWT_AUDIENCE", default=None)
FARMBASE_JWT_EMAIL_OVERRIDE = config("FARMBASE_JWT_EMAIL_OVERRIDE", default=None)

FARMBASE_JWT_SECRET = config("FARMBASE_JWT_SECRET", default=None)
FARMBASE_JWT_ALG = config("FARMBASE_JWT_ALG", default="HS256")
FARMBASE_JWT_EXP = config("FARMBASE_JWT_EXP", cast=int, default=86400)  # Seconds


FARMBASE_AUTHENTICATION_PROVIDER_HEADER_NAME = config(
    "FARMBASE_AUTHENTICATION_PROVIDER_HEADER_NAME", default="remote-user"
)

FARMBASE_AUTHENTICATION_DEFAULT_USER = config("FARMBASE_AUTHENTICATION_DEFAULT_USER", default="farmbase@example.com")

FARMBASE_AUTHENTICATION_PROVIDER_PKCE_JWKS = config("FARMBASE_AUTHENTICATION_PROVIDER_PKCE_JWKS", default=None)

FARMBASE_PKCE_DONT_VERIFY_AT_HASH = config("FARMBASE_PKCE_DONT_VERIFY_AT_HASH", default=False)

# static files
DEFAULT_STATIC_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), os.path.join("static", "farmbase", "dist")
)
STATIC_DIR = config("STATIC_DIR", default=DEFAULT_STATIC_DIR)

# sentry middleware
SENTRY_ENABLED = config("SENTRY_ENABLED", default="")
SENTRY_DSN = config("SENTRY_DSN", default="")
SENTRY_APP_KEY = config("SENTRY_APP_KEY", default="")
SENTRY_TAGS = config("SENTRY_TAGS", default="")

# database
DATABASE_HOSTNAME = config("DATABASE_HOSTNAME")
DATABASE_USER = config("DATABASE_USER")
DATABASE_PASSWORD = config("DATABASE_PASSWORD", cast=Secret)
_QUOTED_DATABASE_PASSWORD = parse.quote(str(DATABASE_PASSWORD))
DATABASE_NAME = config("DATABASE_NAME", default="farmbase")
DATABASE_PORT = config("DATABASE_PORT", default="5432")
DATABASE_ENGINE_MAX_OVERFLOW = config("DATABASE_ENGINE_MAX_OVERFLOW", cast=int, default=10)
# Deal with DB disconnects
# https://docs.sqlalchemy.org/en/20/core/pooling.html#pool-disconnects
DATABASE_ENGINE_POOL_PING = config("DATABASE_ENGINE_POOL_PING", default=False)
DATABASE_ENGINE_POOL_RECYCLE = config("DATABASE_ENGINE_POOL_RECYCLE", cast=int, default=3600)
DATABASE_ENGINE_POOL_SIZE = config("DATABASE_ENGINE_POOL_SIZE", cast=int, default=20)
DATABASE_ENGINE_POOL_TIMEOUT = config("DATABASE_ENGINE_POOL_TIMEOUT", cast=int, default=30)
SQLALCHEMY_DATABASE_URI = f"postgresql+asyncpg://{DATABASE_USER}:{_QUOTED_DATABASE_PASSWORD}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"
SQLALCHEMY_DATABASE_SYNC_URI = f"postgresql+psycopg2://{DATABASE_USER}:{_QUOTED_DATABASE_PASSWORD}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"

ALEMBIC_CORE_REVISION_PATH = config(
    "ALEMBIC_CORE_REVISION_PATH",
    default=f"{os.path.dirname(os.path.realpath(__file__))}/database/revisions/core",
)
ALEMBIC_TENANT_REVISION_PATH = config(
    "ALEMBIC_TENANT_REVISION_PATH",
    default=f"{os.path.dirname(os.path.realpath(__file__))}/database/revisions/tenant",
)
ALEMBIC_INI_PATH = config(
    "ALEMBIC_INI_PATH",
    default=f"{os.path.dirname(os.path.realpath(__file__))}/alembic.ini",
)

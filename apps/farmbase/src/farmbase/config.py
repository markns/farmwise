import logging
import os
from typing import List

from pydantic import BaseModel
from starlette.config import Config
from starlette.datastructures import Secret

log = logging.getLogger(__name__)


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


LOG_LEVEL = config("LOG_LEVEL", default=logging.WARNING)
ENV = config("ENV", default="local")


FARMBASE_UI_URL = config("FARMBASE_UI_URL", default="http://localhost:8080")
FARMBASE_ENCRYPTION_KEY = config("FARMBASE_ENCRYPTION_KEY", cast=Secret)


# static files
DEFAULT_STATIC_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), os.path.join("static", "farmbase", "dist")
)
STATIC_DIR = config("STATIC_DIR", default=DEFAULT_STATIC_DIR)

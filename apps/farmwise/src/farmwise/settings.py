import os
from typing import Any

from agents import set_default_openai_key
from dotenv import find_dotenv
from pydantic import (
    HttpUrl,
    SecretStr,
    TypeAdapter,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def check_str_is_http(x: str) -> str:
    http_url_adapter = TypeAdapter(HttpUrl)
    return str(http_url_adapter.validate_python(x))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        validate_default=False,
    )
    MODE: str | None = None
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    OPENAI_API_KEY: SecretStr
    FARMBASE_ENDPOINT: str
    FARMBASE_API_KEY: SecretStr
    ISDA_USERNAME: str
    ISDA_PASSWORD: SecretStr
    WHATSAPP_TOKEN: str
    WHATSAPP_PHONE_ID: str
    WHATSAPP_CALLBACK_URL: str
    WHATSAPP_VERIFY_TOKEN: str
    WHATSAPP_APP_ID: int
    WHATSAPP_APP_SECRET: str
    GCS_BUCKET: str = "gs://farmwise_media"

    UPSTASH_REDIS_REST_URL: str
    UPSTASH_REDIS_REST_TOKEN: str
    SESSION_TTL_SECS: int = 7200  # default 2 hour session

    def is_dev(self) -> bool:
        return self.MODE == "dev"

    def model_post_init(self, __context: Any) -> None:
        set_default_openai_key(self.OPENAI_API_KEY.get_secret_value())


settings = Settings()

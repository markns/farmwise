from dotenv import find_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        validate_default=False,
    )
    OPENAI_API_KEY: SecretStr

    WHATSAPP_TOKEN: str
    WHATSAPP_PHONE_ID: str

    TEMPORAL_HOST: str
    TEMPORAL_PORT: int = 7233

    # noinspection PyPep8Naming
    @property
    def TEMPORAL_ENDPOINT(self) -> str:
        return f"{self.TEMPORAL_HOST}:{self.TEMPORAL_PORT}"

settings = Settings()

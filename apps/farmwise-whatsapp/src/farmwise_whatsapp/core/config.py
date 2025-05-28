from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="/Users/markns/workspace/farmwise/.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    AGENT_URL: str
    DEBUG: bool
    WHATSAPP_TOKEN: str
    WHATSAPP_PHONE_ID: str
    WHATSAPP_CALLBACK_URL: str
    DOWNLOAD_DIR: str
    MEDIA_SERVER: str

    # class Config:
    #     env_file = ".env"  # Load environment variables from .env


settings = Settings()  # type: ignore

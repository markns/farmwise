import os
from typing import Any
from urllib import parse

from dotenv import find_dotenv
from loguru import logger
from pydantic import AnyHttpUrl, Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Helper for file-path based defaults ---
# Pydantic models are defined at import time, so we calculate the base directory here.
_BASE_DIR = os.path.dirname(os.path.realpath(__file__))


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    Pydantic v2 automatically finds and loads the .env file.
    """

    # Pydantic v2 model configuration.
    # It replaces the `Config` class from Pydantic v1.
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- General ---
    FARMBASE_UI_URL: AnyHttpUrl = Field(default="http://localhost:8080")
    FARMBASE_ENCRYPTION_KEY: SecretStr
    FARMBASE_API_KEY: SecretStr
    OPENAI_API_KEY: SecretStr

    # --- Security ---
    ALLOWED_ORIGINS: list[str] = Field(default=["http://localhost:8080", "http://127.0.0.1:8080"])

    # --- Database ---
    DATABASE_HOSTNAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: SecretStr
    DATABASE_NAME: str = "farmbase"
    DATABASE_PORT: int = 5432
    DATABASE_ENGINE_MAX_OVERFLOW: int = 10
    DATABASE_ENGINE_POOL_PING: bool = False
    DATABASE_ENGINE_POOL_RECYCLE: int = 3600
    DATABASE_ENGINE_POOL_SIZE: int = 20
    DATABASE_ENGINE_POOL_TIMEOUT: int = 30

    # Pydantic will automatically read the environment variable
    # 'GOOGLE_APPLICATION_CREDENTIALS' into this attribute.
    # It's optional so the app doesn't crash if it's not set.
    google_application_credentials: str | None = None

    @computed_field
    @property
    def sqlalchemy_database_uri(self) -> str:
        """
        Construct the asynchronous database URI from other settings.
        This is a computed field and does not need to be set in the environment.
        """
        # .get_secret_value() is used to access the raw string from a SecretStr
        quoted_password = parse.quote(self.DATABASE_PASSWORD.get_secret_value())

        # If the hostname is a path (for a Unix socket), don't include the port.
        if self.DATABASE_HOSTNAME.startswith("/"):
            host_and_port = self.DATABASE_HOSTNAME
        # Otherwise, it's a regular network host, so include the port.
        else:
            host_and_port = f"{self.DATABASE_HOSTNAME}:{self.DATABASE_PORT}"

        return f"postgresql+asyncpg://{self.DATABASE_USER}:{quoted_password}@{host_and_port}/{self.DATABASE_NAME}"

    @computed_field
    @property
    def sqlalchemy_database_sync_uri(self) -> str:
        """
        Construct the synchronous database URI from other settings.
        """
        quoted_password = parse.quote(self.DATABASE_PASSWORD.get_secret_value())
        return (
            f"postgresql+psycopg2://{self.DATABASE_USER}:{quoted_password}"
            f"@{self.DATABASE_HOSTNAME}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    # --- Alembic ---
    # Default values are calculated using the _BASE_DIR helper defined at the top.
    ALEMBIC_CORE_REVISION_PATH: str = os.path.join(_BASE_DIR, "database/revisions/core")
    ALEMBIC_TENANT_REVISION_PATH: str = os.path.join(_BASE_DIR, "database/revisions/tenant")
    ALEMBIC_INI_PATH: str = os.path.join(_BASE_DIR, "alembic.ini")

    def model_post_init(self, __context: Any) -> None:
        """
        This method runs after the model is initialized.
        It's the perfect place to set the os.environ variable.
        """
        if self.google_application_credentials:
            logger.debug("Found GAC path in settings, setting environment variable for other libraries...")
            # Set the environment variable for libraries like gcsfs and GDAL to find.
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.google_application_credentials
        else:
            # This allows the app to still work if the variable is already
            # set in the environment before the app starts (e.g., in Docker).
            logger.debug("GAC path not defined in .env or settings. Relying on pre-existing environment.")


# Create a single instance of the settings to be imported by other modules
settings = Settings()

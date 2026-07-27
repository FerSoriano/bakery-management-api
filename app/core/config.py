from typing import Annotated, Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic-settings looks for these variables in the .env automatically
    # The field name must exactly match the environment variable
    database_url: str
    db_echo: bool = False  # echo=True will print the generated SQL in the terminal (debugging)

    # Origins allowed to call the API from a browser.
    # NoDecode disables the automatic JSON parsing that pydantic-settings applies
    # to complex types, so the validator below receives the raw comma-separated string.
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",  # vite dev server
        "http://127.0.0.1:5173",  # vite dev server (same host, different origin)
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: Any) -> Any:
        """
        Accept a comma-separated string from the environment, and leave an
        already-parsed list (the default) untouched.
        """
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Single instance that is imported throughout the app
settings = Settings()

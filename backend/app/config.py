"""Application settings, loaded from environment variables / .env."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Anthropic ---
    anthropic_api_key: str = ""
    # NOTE: Model IDs change over time. Override with ANTHROPIC_MODEL and check
    # https://docs.claude.com for the current list of model identifiers.
    anthropic_model: str = "claude-3-5-sonnet-latest"
    max_tokens: int = 1500

    # --- App ---
    app_env: str = "development"
    # Comma-separated list of allowed CORS origins.
    allowed_origins: str = "http://localhost:3000"

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()

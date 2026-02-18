from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Loads settings from environment variables and `.env` in local development.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "RateGuard API"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    rate_limit_per_minute: int = 60
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/rateguard"
    api_keys: str = "local-dev-key"

    @property
    def parsed_api_keys(self) -> set[str]:
        # Comma-separated keys are normalized to a lookup set for O(1) membership checks.
        return {key.strip() for key in self.api_keys.split(",") if key.strip()}


@lru_cache
def get_settings() -> Settings:
    # Cached to avoid re-parsing env vars on every dependency call.
    return Settings()

"""
Centralized application settings.

All configuration is read from environment variables (see .env.example).
Nothing here should be hardcoded per-environment — that's what lets the same
code run locally, in a hosted demo, and eventually in AWS (Section 7.3)
without code changes.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    PROJECT_NAME: str = "TalentSync"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True

    # --- Database ---
    DATABASE_URL: str

    # --- Auth / JWT ---
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24h — generous for demo purposes

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,https://dhrutirajguru.github.io"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor. Use this (not Settings() directly) everywhere,
    so the .env file is only parsed once per process.
    """
    return Settings()


settings = get_settings()

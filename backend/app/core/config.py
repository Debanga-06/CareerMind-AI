"""
Application configuration.

All configuration is loaded from environment variables (via a local .env
file during development). Nothing sensitive is hardcoded, and nothing
sensitive should ever be echoed back in an API response.
"""
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings, populated from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- App ---
    APP_NAME: str = "CareerGraph AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"

    # --- CORS ---
    # Comma separated list of allowed origins for local React dev servers.
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,https://carrier-mind-ai.vercel.app"

    # --- SerpApi ---
    # Required. Never returned in any response body/schema.
    SERPAPI_API_KEY: str = Field(default="")
    SERPAPI_BASE_URL: str = "https://serpapi.com/search"
    SERPAPI_TIMEOUT_SECONDS: float = 20.0
    SERPAPI_MAX_RETRIES: int = 2

    # --- Caching (simple in-memory cache for MVP; see services/cache_service.py) ---
    SERPAPI_CACHE_TTL_SECONDS: int = 60 * 30  # 30 minutes

    # --- Rate limiting (simple in-process limiter for MVP) ---
    RATE_LIMIT_REQUESTS: int = 30
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # --- Database ---
    # Works with local Postgres or a Supabase Postgres connection string.
    DATABASE_URL: str = "sqlite:///./careergraph_dev.db"

    # --- JWT Auth ---
    JWT_SECRET_KEY: str = "change-me-in-env"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # --- AI provider abstraction (used in later stages) ---
    AI_PROVIDER: str = "none"  # "none" | "anthropic" | "openai" | ...
    AI_API_KEY: str = ""
    AI_MODEL: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor so we parse the environment only once."""
    return Settings()

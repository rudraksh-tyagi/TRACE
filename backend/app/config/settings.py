"""
TRACE application configuration.

Configuration is loaded from environment variables and .env.

Example:

    USE_MOCK_DATA=true
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global TRACE backend configuration.
    """

    # ========================================================
    # APPLICATION
    # ========================================================

    system_name: str = Field(
        default="TRACE Marine Oil Spill Intelligence System",
        description="Application name.",
    )

    system_version: str = Field(
        default="TRACE-0.3.0",
        description="Backend system version.",
    )

    # ========================================================
    # DEMO MODE
    # ========================================================

    use_mock_data: bool = Field(
        default=True,
        description=(
            "When enabled, API endpoints can fall back to "
            "static mock data when live pipeline state is "
            "unavailable."
        ),
    )

    # ========================================================
    # LOGGING
    # ========================================================

    log_level: str = Field(
        default="INFO",
        description="Application logging level.",
    )

    # ========================================================
    # CORS
    # ========================================================

    cors_origins: str = Field(
        default="*",
        description=(
            "Comma-separated list of allowed frontend origins."
        ),
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        """
        Convert comma-separated CORS origins into a list.
        """

        if self.cors_origins.strip() == "*":
            return ["*"]

        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """
    Return cached application settings.
    """

    return Settings()


settings = get_settings()
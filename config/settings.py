from functools import lru_cache
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application and test execution configuration settings."""

    # Application Target
    BASE_URL: str = Field(
        default="https://www.automationexercise.com",
        description="Target Base URL of the web application",
    )

    # Browser Execution Settings
    BROWSER: Literal["chromium", "firefox", "webkit"] = Field(
        default="chromium",
        description="Browser engine to run tests against",
    )
    HEADLESS: bool = Field(
        default=True,
        description="Run browser in headless or headed mode",
    )
    SLOW_MO: int = Field(
        default=0,
        description="Delay in milliseconds between actions for debugging",
    )
    DEFAULT_TIMEOUT: int = Field(
        default=15000,
        description="Default timeout in milliseconds for Playwright operations",
    )

    # Viewport Settings
    VIEWPORT_WIDTH: int = Field(default=1920, description="Browser viewport width")
    VIEWPORT_HEIGHT: int = Field(default=1080, description="Browser viewport height")

    # Observability & Diagnostics
    RECORD_VIDEO: Literal["off", "on", "retain-on-failure"] = Field(
        default="retain-on-failure",
        description="Record video during test runs",
    )
    RECORD_TRACE: Literal["off", "on", "retain-on-failure"] = Field(
        default="retain-on-failure",
        description="Record Playwright trace for test failures",
    )
    SCREENSHOT_ON_FAILURE: bool = Field(
        default=True,
        description="Capture full-page screenshot upon test failure",
    )

    # Logging Configuration
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging verbosity (TRACE, DEBUG, INFO, WARNING, ERROR)",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Retrieve singleton instance of cached application settings."""
    return Settings()


# Export standard singleton
settings = get_settings()


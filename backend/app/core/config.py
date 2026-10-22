"""Application configuration module using pydantic-settings."""

import sys
from pathlib import Path

from pydantic import ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine repository root directory dynamically (backend/app/core -> project root)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_PATH = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings loaded strictly from environment variables or .env."""

    ENVIRONMENT: str = "development"
    PORT: int = 8001
    DATABASE_URL: str
    TEST_DATABASE_URL: str
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    COOKIE_SECURE: bool | None = None
    TRUSTED_PROXY: bool = False
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_LOGIN_FAIL_LIMIT: int = 5
    RATE_LIMIT_LOGIN_FAIL_WINDOW: int = 900
    RATE_LIMIT_LOGIN_IP_LIMIT: int = 20
    RATE_LIMIT_LOGIN_IP_WINDOW: int = 900
    RATE_LIMIT_REGISTER_LIMIT: int = 10
    RATE_LIMIT_REGISTER_WINDOW: int = 3600
    RATE_LIMIT_CHANGE_PASSWORD_LIMIT: int = 5
    RATE_LIMIT_CHANGE_PASSWORD_WINDOW: int = 900

    @model_validator(mode="after")
    def set_cookie_secure_default(self) -> "Settings":
        """Default COOKIE_SECURE to True in production, False otherwise."""
        if self.COOKIE_SECURE is None:
            self.COOKIE_SECURE = self.ENVIRONMENT == "production"
        return self

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH) if ENV_PATH.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )


def load_settings(env_file_path: Path | str | None = None) -> Settings:
    """Load settings from environment or .env, failing with a clear message if missing."""
    try:
        if env_file_path is not None:
            resolved_path = Path(env_file_path)
            return Settings(_env_file=str(resolved_path) if resolved_path.exists() else None)
        return Settings()
    except ValidationError as exc:
        missing_fields = [
            str(err["loc"][0]) for err in exc.errors() if err.get("type") == "missing"
        ]
        missing_str = ", ".join(missing_fields) if missing_fields else str(exc)
        error_msg = (
            f"\n{'=' * 78}\n"
            f"[FATAL CONFIGURATION ERROR] Missing required setting(s): {missing_str}\n"
            "Please copy '.env.example' to '.env' at the project root and configure settings:\n"
            "  PowerShell: Copy-Item .env.example .env\n"
            "  Bash:       cp .env.example .env\n"
            f"{'=' * 78}\n"
        )
        sys.stderr.write(error_msg)
        raise RuntimeError(
            f"Missing required environment variable(s): {missing_str}. "
            "Please copy '.env.example' to '.env' at the project root."
        ) from exc


settings = load_settings()

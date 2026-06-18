from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ directory (two levels up from this file: app/core/config.py -> backend/)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables (and optionally a .env file).

    DATABASE_URL defaults to a local SQLite file for this first vertical slice.
    It's deliberately read from an env var so we can swap to Postgres later
    (e.g. postgresql+psycopg://user:pass@host/db) without touching any code that
    consumes `settings.database_url` — just change the env var.
    """

    database_url: str = f"sqlite:///{BACKEND_DIR / 'finance.db'}"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

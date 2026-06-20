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

    # AI agent (chat assistant)
    openai_api_key: str | None = None

    # Plaid (bank linking) — get free Sandbox keys at https://dashboard.plaid.com/signup
    plaid_client_id: str | None = None
    plaid_secret: str | None = None
    plaid_env: str = "sandbox"

    # Fernet key used to encrypt Plaid access tokens at rest.
    # Generate one with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    fernet_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def openai_configured(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def plaid_configured(self) -> bool:
        return bool(self.plaid_client_id and self.plaid_secret)


settings = Settings()

"""
Thin wrapper around `cryptography.fernet.Fernet` used to encrypt/decrypt Plaid
access tokens before they're persisted in `Institution.plaid_access_token_encrypted`.

Deliberately lazy about `settings.fernet_key`: importing this module (and the
rest of the app) must succeed even if FERNET_KEY hasn't been set in .env yet,
so unrelated routes like /health keep working. The error only surfaces when
someone actually tries to encrypt/decrypt without a key configured.
"""
from cryptography.fernet import Fernet

from app.core.config import settings


class FernetKeyNotConfigured(RuntimeError):
    pass


def _get_fernet() -> Fernet:
    if not settings.fernet_key:
        raise FernetKeyNotConfigured(
            "FERNET_KEY is not set in backend/.env — generate one with: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    return Fernet(settings.fernet_key.encode())


def encrypt(value: str) -> str:
    """Encrypt a plaintext string (e.g. a Plaid access token) for storage."""
    return _get_fernet().encrypt(value.encode()).decode()


def decrypt(token: str) -> str:
    """Decrypt a value previously produced by `encrypt`."""
    return _get_fernet().decrypt(token.encode()).decode()

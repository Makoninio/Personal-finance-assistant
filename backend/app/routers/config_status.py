from fastapi import APIRouter

from app.core.config import settings
from app.schemas import ConfigStatus

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/status", response_model=ConfigStatus)
def status() -> ConfigStatus:
    """Lets the frontend Settings page show which integrations are wired up,
    without ever exposing the actual secret values."""
    return ConfigStatus(
        openai_configured=settings.openai_configured,
        plaid_configured=settings.plaid_configured,
    )

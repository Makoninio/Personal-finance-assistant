from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Account, Institution
from app.schemas import AccountRead
from app.services import plaid_service

router = APIRouter(prefix="/plaid", tags=["plaid"])


class LinkTokenResponse(BaseModel):
    link_token: str


class ExchangePublicTokenRequest(BaseModel):
    public_token: str


class SyncResponse(BaseModel):
    added: int
    modified: int
    removed: int


def _accounts_for_institution(db: Session, institution_id: int) -> list[Account]:
    rows = db.execute(
        select(Account).where(Account.institution_id == institution_id)
    ).scalars().all()
    return list(rows)


def _account_read(account: Account) -> AccountRead:
    return AccountRead(
        id=account.id,
        institution_id=account.institution_id,
        institution_name=account.institution.name if account.institution else None,
        plaid_account_id=account.plaid_account_id,
        name=account.name,
        type=account.type,
        mask=account.mask,
        current_balance=float(account.current_balance) if account.current_balance is not None else None,
        available_balance=float(account.available_balance) if account.available_balance is not None else None,
    )


@router.post("/create_link_token", response_model=LinkTokenResponse)
def create_link_token() -> LinkTokenResponse:
    try:
        token = plaid_service.create_link_token()
    except plaid_service.PlaidNotConfigured as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return LinkTokenResponse(link_token=token)


@router.post("/exchange_public_token", response_model=list[AccountRead])
def exchange_public_token(
    body: ExchangePublicTokenRequest, db: Session = Depends(get_db)
) -> list[AccountRead]:
    try:
        institution = plaid_service.exchange_public_token(body.public_token, db)
    except plaid_service.PlaidNotConfigured as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    accounts = _accounts_for_institution(db, institution.id)
    return [_account_read(account) for account in accounts]


@router.post("/sync/{institution_id}", response_model=SyncResponse)
def sync_institution(institution_id: int, db: Session = Depends(get_db)) -> SyncResponse:
    """Manually re-trigger a sync for one institution.

    Stand-in for webhook-driven sync tonight: a real Plaid webhook needs a
    publicly reachable HTTPS endpoint, which isn't practical for a localhost
    demo without tunneling (e.g. ngrok) — out of scope for tonight.
    """
    institution = db.get(Institution, institution_id)
    if institution is None:
        raise HTTPException(status_code=404, detail="Institution not found")

    try:
        result = plaid_service.sync_institution(institution, db)
    except plaid_service.PlaidNotConfigured as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return SyncResponse(**result)

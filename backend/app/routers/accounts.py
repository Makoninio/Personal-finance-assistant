from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Account
from app.schemas import AccountRead

router = APIRouter()


@router.get("/accounts", response_model=list[AccountRead])
def list_accounts(db: Session = Depends(get_db)) -> list[AccountRead]:
    accounts = db.execute(select(Account)).scalars().all()
    return [
        AccountRead(
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
        for account in accounts
    ]

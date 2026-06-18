from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Transaction
from app.schemas import TransactionRead

router = APIRouter()


@router.get("/transactions", response_model=list[TransactionRead])
def list_transactions(db: Session = Depends(get_db)) -> list[Transaction]:
    transactions = db.execute(select(Transaction).order_by(Transaction.date)).scalars().all()
    return list(transactions)

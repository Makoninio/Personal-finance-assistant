from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Budget
from app.schemas import BudgetCreate, BudgetRead
from app.services.insights_service import get_category_breakdown

router = APIRouter(prefix="/budgets", tags=["budgets"])


def _spent_by_category(db: Session) -> dict[str, float]:
    return {row["category"]: row["total_spent"] for row in get_category_breakdown(db)}


@router.get("", response_model=list[BudgetRead])
def list_budgets(db: Session = Depends(get_db)) -> list[BudgetRead]:
    budgets = db.execute(select(Budget)).scalars().all()
    spent = _spent_by_category(db)
    return [
        BudgetRead(
            id=b.id,
            category_id=b.category_id,
            category_name=b.category.name if b.category else None,
            period=b.period,
            amount_limit=float(b.amount_limit),
            effective_from=b.effective_from,
            spent_this_period=spent.get(b.category.name if b.category else "", 0.0),
        )
        for b in budgets
    ]


@router.post("", response_model=BudgetRead)
def create_budget(payload: BudgetCreate, db: Session = Depends(get_db)) -> BudgetRead:
    from datetime import date

    budget = Budget(
        category_id=payload.category_id,
        amount_limit=payload.amount_limit,
        period=payload.period,
        effective_from=date.today().replace(day=1),
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)

    spent = _spent_by_category(db)
    return BudgetRead(
        id=budget.id,
        category_id=budget.category_id,
        category_name=budget.category.name if budget.category else None,
        period=budget.period,
        amount_limit=float(budget.amount_limit),
        effective_from=budget.effective_from,
        spent_this_period=spent.get(budget.category.name if budget.category else "", 0.0),
    )


@router.delete("/{budget_id}", status_code=204)
def delete_budget(budget_id: int, db: Session = Depends(get_db)) -> None:
    budget = db.get(Budget, budget_id)
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(budget)
    db.commit()

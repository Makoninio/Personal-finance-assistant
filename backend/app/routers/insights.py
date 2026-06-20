from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.services import insights_service

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)) -> dict:
    return insights_service.get_summary(db)

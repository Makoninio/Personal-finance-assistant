from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas import SubscriptionRead
from app.services import subscription_service

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("", response_model=list[SubscriptionRead])
def list_subscriptions(db: Session = Depends(get_db)) -> list:
    return subscription_service.list_subscriptions(db)


@router.post("/detect", response_model=list[SubscriptionRead])
def detect(db: Session = Depends(get_db)) -> list:
    subscription_service.detect_subscriptions(db)
    return subscription_service.list_subscriptions(db)

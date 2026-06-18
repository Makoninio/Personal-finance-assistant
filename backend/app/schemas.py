from datetime import date as date_type
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TransactionRead(BaseModel):
    """Response schema for a transaction, with the category name flattened in for convenience."""

    id: int
    date: date_type
    amount: float
    description: str
    type: str
    category_id: int | None = None
    category_name: str | None = None
    merchant_id: int | None = None
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

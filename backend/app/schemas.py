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
    account_id: int | None = None
    source: str
    pending: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionRead(BaseModel):
    id: int
    merchant_name: str
    amount: float
    cadence: str
    first_seen_date: date_type
    last_seen_date: date_type
    status: str
    detected_by: str

    model_config = ConfigDict(from_attributes=True)


class BudgetRead(BaseModel):
    id: int
    category_id: int
    category_name: str | None = None
    period: str
    amount_limit: float
    effective_from: date_type
    spent_this_period: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class BudgetCreate(BaseModel):
    category_id: int
    amount_limit: float
    period: str = "monthly"


class AccountRead(BaseModel):
    id: int
    institution_id: int
    institution_name: str | None = None
    plaid_account_id: str
    name: str
    type: str | None = None
    mask: str | None = None
    current_balance: float | None = None
    available_balance: float | None = None

    model_config = ConfigDict(from_attributes=True)


class ConfigStatus(BaseModel):
    openai_configured: bool
    plaid_configured: bool


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str

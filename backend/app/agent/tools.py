"""
LangChain tools for the personal finance chat agent.

Each tool opens and closes its own short-lived DB session via `SessionLocal`
(rather than FastAPI's `Depends(get_db)`), because tools execute inside the
LangGraph agent's tool-calling loop, outside of any HTTP request context.

These tools are thin wrappers around the existing service layer
(`app.services.insights_service`, `app.services.subscription_service`) and a
direct SQLAlchemy query for raw transaction lookups — they intentionally do
not reimplement any analytics logic.
"""
from datetime import date as date_type
from datetime import datetime

from langchain_core.tools import tool
from sqlalchemy import select

from app.db.base import SessionLocal
from app.db.models import Category, Transaction
from app.services import insights_service, subscription_service


@tool
def get_spending_summary() -> dict:
    """Get a full snapshot of the user's finances: net worth, income vs.
    expenses, spending by category, monthly trends, top merchants, spending
    velocity (daily/weekly/monthly averages), a financial health score, and
    budget recommendations.

    Call this when the user asks a broad question like "how am I doing
    financially?", "what's my net worth?", "where does my money go?", or
    when you need general context before answering a more specific question.
    """
    db = SessionLocal()
    try:
        return insights_service.get_summary(db)
    finally:
        db.close()


@tool
def query_transactions(
    category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    min_amount: float | None = None,
) -> list[dict]:
    """Look up individual transactions, optionally filtered by category name,
    a date range, and/or a minimum absolute amount. Returns up to 50 matching
    transactions with date, description, amount, type, and category.

    Call this when the user asks about specific transactions, e.g. "how much
    did I spend on groceries?", "show me my Spotify charges", "what did I
    spend last month?", or "what are my biggest purchases?" (use min_amount
    for that last one).

    Args:
        category: Filter by category name (case-insensitive partial match),
            e.g. "Groceries", "Entertainment". Omit to include all categories.
        start_date: ISO date string (YYYY-MM-DD) — only include transactions
            on or after this date. Omit for no lower bound.
        end_date: ISO date string (YYYY-MM-DD) — only include transactions on
            or before this date. Omit for no upper bound.
        min_amount: Only include transactions whose absolute amount is at
            least this value. Useful for finding large purchases.
    """
    db = SessionLocal()
    try:
        query = select(Transaction)

        if category:
            query = query.join(Category, Transaction.category_id == Category.id).where(
                Category.name.ilike(f"%{category}%")
            )

        if start_date:
            try:
                parsed_start = datetime.strptime(start_date, "%Y-%m-%d").date()
                query = query.where(Transaction.date >= parsed_start)
            except ValueError:
                pass

        if end_date:
            try:
                parsed_end = datetime.strptime(end_date, "%Y-%m-%d").date()
                query = query.where(Transaction.date <= parsed_end)
            except ValueError:
                pass

        query = query.order_by(Transaction.date.desc()).limit(50)
        rows = db.execute(query).scalars().all()

        results = []
        for t in rows:
            if min_amount is not None and abs(float(t.amount)) < min_amount:
                continue
            results.append(
                {
                    "date": t.date.isoformat() if isinstance(t.date, date_type) else str(t.date),
                    "description": t.description,
                    "amount": float(t.amount),
                    "type": t.type,
                    "category": t.category_name or "Uncategorized",
                }
            )
        return results[:50]
    finally:
        db.close()


@tool
def get_subscriptions() -> list[dict]:
    """Detect and list recurring subscriptions (e.g. Spotify, Netflix, gym
    memberships) based on transaction history — merchants charged a
    consistent amount on a roughly monthly cadence.

    Call this when the user asks about subscriptions, recurring charges, or
    things they might want to cancel.
    """
    db = SessionLocal()
    try:
        detected = subscription_service.detect_subscriptions(db, persist=True)
        subs = subscription_service.list_subscriptions(db)
        return [
            {
                "merchant_name": s.merchant_name,
                "amount": float(s.amount),
                "cadence": s.cadence,
                "first_seen_date": s.first_seen_date.isoformat(),
                "last_seen_date": s.last_seen_date.isoformat(),
                "status": s.status,
            }
            for s in subs
        ] or detected
    finally:
        db.close()


@tool
def get_financial_health_score() -> dict:
    """Get the user's overall financial health score (0-100) along with the
    contributing factors (e.g. net worth, expense ratio, spending velocity,
    number of subscriptions).

    Call this when the user asks "how healthy are my finances?" or "give me
    a financial health score."
    """
    db = SessionLocal()
    try:
        return insights_service.get_financial_health_score(db)
    finally:
        db.close()


@tool
def get_monthly_trends() -> list[dict]:
    """Get month-by-month totals of income, expenses, and net savings.

    Call this when the user asks about trends over time, e.g. "how has my
    spending changed?", "am I saving more than last month?", or "show me my
    monthly trends."
    """
    db = SessionLocal()
    try:
        return insights_service.get_monthly_trends(db)
    finally:
        db.close()


ALL_TOOLS = [
    get_spending_summary,
    query_transactions,
    get_subscriptions,
    get_financial_health_score,
    get_monthly_trends,
]

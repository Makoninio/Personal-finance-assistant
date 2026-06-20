"""
Financial insights/analytics, ported from the legacy finance-assistant/backend/insights.py
(originally pandas-on-a-DataFrame; now reads straight from the transactions table).
"""
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Transaction
from app.services.subscription_service import detect_subscriptions


def _transactions_df(db: Session) -> pd.DataFrame:
    rows = db.execute(select(Transaction)).scalars().all()
    if not rows:
        return pd.DataFrame(columns=["date", "amount", "type", "category", "description"])

    df = pd.DataFrame(
        [
            {
                "date": t.date,
                "amount": float(t.amount),
                "type": t.type,
                "category": t.category_name or "Uncategorized",
                "description": t.description,
            }
            for t in rows
        ]
    )
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df


def get_net_worth_snapshot(db: Session) -> dict:
    df = _transactions_df(db)
    if df.empty:
        return {"total_income": 0.0, "total_expenses": 0.0, "net_worth": 0.0}

    total_income = float(df[df["type"] == "credit"]["amount"].sum())
    total_expenses = float(abs(df[df["type"] == "debit"]["amount"].sum()))
    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_worth": round(total_income - total_expenses, 2),
    }


def get_category_breakdown(db: Session) -> list[dict]:
    df = _transactions_df(db)
    if df.empty:
        return []

    debit_df = df[df["type"] == "debit"].copy()
    debit_df["amount"] = debit_df["amount"].abs()
    if debit_df.empty:
        return []

    summary = debit_df.groupby("category").agg(
        total_spent=("amount", "sum"),
        transaction_count=("amount", "count"),
        avg_transaction=("amount", "mean"),
    ).round(2)
    summary = summary.sort_values("total_spent", ascending=False)
    summary["percentage"] = (summary["total_spent"] / summary["total_spent"].sum() * 100).round(1)
    return summary.reset_index().to_dict(orient="records")


def get_monthly_trends(db: Session) -> list[dict]:
    df = _transactions_df(db)
    if df.empty:
        return []

    grouped = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0)
    grouped["total_income"] = grouped.get("credit", 0)
    grouped["total_expenses"] = grouped.get("debit", 0).abs()
    grouped["net"] = grouped["total_income"] - grouped["total_expenses"]
    return grouped.reset_index()[["month", "total_income", "total_expenses", "net"]].round(2).to_dict(
        orient="records"
    )


def get_top_merchants(db: Session, limit: int = 10) -> list[dict]:
    df = _transactions_df(db)
    if df.empty:
        return []

    debit_df = df[df["type"] == "debit"].copy()
    debit_df["amount"] = debit_df["amount"].abs()
    if debit_df.empty:
        return []

    summary = debit_df.groupby("description").agg(
        total_spent=("amount", "sum"),
        transaction_count=("amount", "count"),
        avg_transaction=("amount", "mean"),
    ).round(2)
    summary = summary.sort_values("total_spent", ascending=False).head(limit)
    return summary.reset_index().to_dict(orient="records")


def get_spending_velocity(db: Session) -> dict:
    df = _transactions_df(db)
    if df.empty:
        return {"daily_avg": 0.0, "weekly_avg": 0.0, "monthly_avg": 0.0}

    days = (df["date"].max() - df["date"].min()).days + 1
    total_spending = float(abs(df[df["type"] == "debit"]["amount"].sum()))
    daily_avg = total_spending / days if days > 0 else 0.0
    return {
        "daily_avg": round(daily_avg, 2),
        "weekly_avg": round(daily_avg * 7, 2),
        "monthly_avg": round(daily_avg * 30, 2),
    }


def get_financial_health_score(db: Session) -> dict:
    df = _transactions_df(db)
    if df.empty:
        return {"score": 0, "factors": [], "subscription_count": 0}

    factors: list[str] = []
    score = 0

    net_worth = get_net_worth_snapshot(db)
    if net_worth["net_worth"] > 0:
        score += 40
        factors.append("Positive net worth")
    elif net_worth["net_worth"] > -1000:
        score += 20
        factors.append("Slightly negative net worth")
    else:
        factors.append("Significantly negative net worth")

    if net_worth["total_income"] > 0:
        expense_ratio = net_worth["total_expenses"] / net_worth["total_income"]
        if expense_ratio < 0.7:
            score += 30
            factors.append("Low expense ratio")
        elif expense_ratio < 0.9:
            score += 20
            factors.append("Moderate expense ratio")
        else:
            factors.append("High expense ratio")

    velocity = get_spending_velocity(db)
    if velocity["daily_avg"] < 50:
        score += 20
        factors.append("Low daily spending")
    elif velocity["daily_avg"] < 100:
        score += 10
        factors.append("Moderate daily spending")
    else:
        factors.append("High daily spending")

    subs = detect_subscriptions(db)
    if len(subs) <= 3:
        score += 10
        factors.append("Few subscriptions")
    elif len(subs) <= 6:
        score += 5
        factors.append("Moderate subscriptions")
    else:
        factors.append("Many subscriptions")

    return {"score": min(score, 100), "factors": factors, "subscription_count": len(subs)}


def get_budget_recommendations(db: Session) -> list[str]:
    recommendations: list[str] = []
    breakdown = get_category_breakdown(db)
    if not breakdown:
        return ["No categorized transactions for recommendations"]

    for row in breakdown:
        if row["percentage"] > 30:
            recommendations.append(
                f"Consider reducing spending in {row['category']} ({row['percentage']:.1f}% of total expenses)"
            )

    subs = detect_subscriptions(db)
    if len(subs) > 5:
        recommendations.append(
            f"Review {len(subs)} recurring subscriptions - consider canceling unused services"
        )

    if not recommendations:
        recommendations.append("Your spending patterns look healthy!")
    return recommendations


def get_summary(db: Session) -> dict:
    """Single aggregate payload for the dashboard page."""
    return {
        "net_worth": get_net_worth_snapshot(db),
        "category_breakdown": get_category_breakdown(db),
        "monthly_trends": get_monthly_trends(db),
        "top_merchants": get_top_merchants(db, limit=5),
        "spending_velocity": get_spending_velocity(db),
        "health_score": get_financial_health_score(db),
        "budget_recommendations": get_budget_recommendations(db),
    }

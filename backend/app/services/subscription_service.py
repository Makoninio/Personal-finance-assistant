"""
Recurring-subscription detection, ported from the legacy
finance-assistant/backend/insights.py::detect_recurring_subscriptions heuristic:
group by description, require low amount variance (<10%) and a ~monthly cadence
(25-35 day average interval between occurrences).
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Subscription, Transaction


def _detect_from_transactions(db: Session) -> list[dict]:
    rows = db.execute(select(Transaction).order_by(Transaction.date)).scalars().all()

    by_description: dict[str, list[Transaction]] = {}
    for t in rows:
        by_description.setdefault(t.description, []).append(t)

    detected: list[dict] = []
    for description, txns in by_description.items():
        if len(txns) < 2:
            continue

        amounts = [abs(float(t.amount)) for t in txns]
        mean_amount = sum(amounts) / len(amounts)
        if mean_amount == 0:
            continue
        variance = (sum((a - mean_amount) ** 2 for a in amounts) / len(amounts)) ** 0.5
        if variance / mean_amount >= 0.1:
            continue

        dates = sorted(t.date for t in txns)
        intervals = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
        avg_interval = sum(intervals) / len(intervals)
        if not (25 <= avg_interval <= 35):
            continue

        detected.append(
            {
                "merchant_name": description,
                "amount": round(mean_amount, 2),
                "cadence": "monthly",
                "first_seen_date": dates[0],
                "last_seen_date": dates[-1],
                "transaction_count": len(txns),
            }
        )

    return sorted(detected, key=lambda s: s["amount"], reverse=True)


def detect_subscriptions(db: Session, persist: bool = True) -> list[dict]:
    """Run the heuristic and (by default) upsert results into the subscriptions table."""
    detected = _detect_from_transactions(db)

    if persist:
        existing = {s.merchant_name: s for s in db.execute(select(Subscription)).scalars().all()}
        for item in detected:
            sub = existing.get(item["merchant_name"])
            if sub is None:
                sub = Subscription(
                    merchant_name=item["merchant_name"],
                    amount=item["amount"],
                    cadence=item["cadence"],
                    first_seen_date=item["first_seen_date"],
                    last_seen_date=item["last_seen_date"],
                    detected_by="heuristic",
                )
                db.add(sub)
            else:
                sub.amount = item["amount"]
                sub.last_seen_date = item["last_seen_date"]
        db.commit()

    return detected


def list_subscriptions(db: Session) -> list[Subscription]:
    return list(db.execute(select(Subscription).order_by(Subscription.amount.desc())).scalars().all())

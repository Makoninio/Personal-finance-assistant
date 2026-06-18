"""
Seed script: creates tables (if needed) and loads the legacy hackathon app's
sample_transactions.csv into the new SQLite DB.

Usage (from inside backend/):
    python -m app.seed
"""
import csv
from datetime import datetime
from pathlib import Path

from app.core.config import BACKEND_DIR
from app.db.base import Base, SessionLocal, engine
from app.db.models import Category, Transaction

# repo root is one level up from backend/
REPO_ROOT = BACKEND_DIR.parent
CSV_PATH = REPO_ROOT / "finance-assistant" / "data" / "sample_transactions.csv"


def seed() -> None:
    Base.metadata.create_all(bind=engine)

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Could not find seed CSV at {CSV_PATH}")

    db = SessionLocal()
    try:
        if db.query(Transaction).first() is not None:
            print("Transactions already seeded, skipping.")
            return

        categories: dict[str, Category] = {
            c.name: c for c in db.query(Category).all()
        }

        with CSV_PATH.open(newline="") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                category_name = (row.get("category") or "").strip()
                category = None
                if category_name:
                    category = categories.get(category_name)
                    if category is None:
                        category = Category(name=category_name)
                        db.add(category)
                        db.flush()
                        categories[category_name] = category

                transaction = Transaction(
                    date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
                    amount=float(row["amount"]),
                    description=row["description"],
                    type=row["type"],
                    category_id=category.id if category else None,
                    merchant_id=None,
                    source="manual_csv",
                )
                db.add(transaction)
                count += 1

        db.commit()
        print(f"Seeded {count} transactions and {len(categories)} categories.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

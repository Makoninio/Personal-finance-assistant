from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base, get_db
from app.db.models import Category, Transaction
from app.main import app

# Isolated in-memory SQLite DB for tests. StaticPool keeps a single connection
# alive for the whole engine so the schema/data persist across sessions.
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

SEED_ROWS = [
    {"description": "SPOTIFY PREMIUM", "category": "Entertainment"},
    {"description": "FOOD LION #1234", "category": "Groceries"},
    {"description": "SALARY DEPOSIT", "category": "Income"},
]


def _seed_test_db():
    db = TestingSessionLocal()
    try:
        categories = {}
        for row in SEED_ROWS:
            cat_name = row["category"]
            if cat_name not in categories:
                category = Category(name=cat_name)
                db.add(category)
                db.flush()
                categories[cat_name] = category

        for i, row in enumerate(SEED_ROWS):
            db.add(
                Transaction(
                    date=date(2024, 1, 15 + i),
                    amount=-12.99,
                    description=row["description"],
                    type="debit",
                    category_id=categories[row["category"]].id,
                    source="manual_csv",
                )
            )
        db.commit()
    finally:
        db.close()


_seed_test_db()

client = TestClient(app)


def test_list_transactions_returns_seeded_rows():
    response = client.get("/transactions")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(SEED_ROWS)

    first = data[0]
    assert first["description"] == SEED_ROWS[0]["description"]
    assert first["category_name"] == SEED_ROWS[0]["category"]
    assert "amount" in first
    assert "date" in first
    assert "type" in first

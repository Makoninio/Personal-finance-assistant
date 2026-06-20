from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base, get_db
from app.main import app

# Isolated in-memory SQLite DB for tests, same pattern as test_transactions.py.
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

client = TestClient(app)


def test_chat_returns_400_when_openai_api_key_unset(monkeypatch):
    """When no OPENAI_API_KEY is configured, /agent/chat should fail gracefully
    with a clear, actionable 400 error instead of crashing or making a network
    call. This doesn't require mocking the LLM at all."""
    monkeypatch.setattr(settings, "openai_api_key", None)

    response = client.post("/agent/chat", json={"message": "How much did I spend on groceries?"})

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "OPENAI_API_KEY" in detail
    assert "backend/.env" in detail

# Personal Finance Assistant — Backend

First vertical slice: a runnable FastAPI backend, SQLite-backed via SQLAlchemy 2.0,
with seeded transactions and a `/transactions` endpoint.

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Seed the database

Loads `finance-assistant/data/sample_transactions.csv` into a local SQLite file
(`backend/finance.db`), creating `Category` rows as needed.

```bash
python -m app.seed
```

Safe to re-run — it skips seeding if transactions already exist. Delete
`finance.db` to start fresh.

## Run the server

```bash
uvicorn app.main:app --reload --port 8000
```

Then:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/transactions
```

## Run tests

```bash
pytest -q
```

Tests use an isolated in-memory SQLite database, independent of `finance.db`.

## Notes

- `DATABASE_URL` env var controls the DB connection string (see
  `app/core/config.py`). Defaults to a local SQLite file. Swappable to Postgres
  later by setting `DATABASE_URL` to a `postgresql+psycopg://...` URL — no code
  changes needed for this slice.
- No auth yet — single implicit demo user, no Plaid, no Postgres, no LangGraph.
  This is intentionally minimal; see the broader project plan for what's next.

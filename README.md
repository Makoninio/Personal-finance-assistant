# Personal Finance Assistant

An AI-powered personal finance app (Rocket Money-style): connect or upload your transactions, get them categorized automatically, and (soon) get proactive insights from an agentic AI layer.

This repo is mid-rebuild. Two things currently live side by side:

- **`finance-assistant/`** — the original hackathon MVP (Streamlit + SQLite + one-shot OpenAI calls for categorization/parsing/explanations). Kept as-is for reference while logic is ported into the new stack.
- **`backend/`** + **`frontend/`** — the new stack being built out: FastAPI + SQLAlchemy (SQLite for now, Postgres-ready) and Next.js (App Router, TypeScript, Tailwind). This is the active development target.

The full architecture, rationale, and week-by-week roadmap (Plaid integration, LangGraph-based agent workflows, scheduled proactive insights, deployment) lives in the project plan — see `/Users/tanaka/.claude/plans/i-m-working-on-a-iterative-lynx.md`. What's running today is the first vertical slice of that plan: a working backend + frontend showing real seeded transaction data end-to-end.

## Running it locally

**Backend** (FastAPI, port 8000):
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed          # creates backend/finance.db and loads sample transactions
uvicorn app.main:app --reload --port 8000
```
Verify: `curl http://localhost:8000/health` → `{"status":"ok"}`, `curl http://localhost:8000/transactions` → seeded transactions as JSON.

**Frontend** (Next.js, port 3000):
```bash
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```
Visit `http://localhost:3000/transactions` — renders live data from the backend when it's running (color-coded amounts, tabular alignment), or a clearly-labeled mock fallback if the backend isn't reachable, so the UI never breaks standalone. The header health badge reflects backend status.

## Current state

- [x] FastAPI backend with SQLite/SQLAlchemy, seeded from `finance-assistant/data/sample_transactions.csv`, `/health` + `/transactions` endpoints, one passing pytest test.
- [x] Next.js frontend with a sidebar shell, a live transactions table, and a backend health indicator.
- [ ] Statement upload (PDF/CSV/image) on the new stack
- [ ] Plaid Sandbox bank-linking integration
- [ ] LangGraph-based agent (chat Q&A, subscription audit, digests, anomaly detection, budget rebalancing)
- [ ] Postgres + Alembic migrations, deployment (Vercel + Railway/Render)

See the project plan for the full design and rationale behind these choices (why LangGraph over CrewAI, why Plaid over Teller, why SQL over a vector store, etc.).

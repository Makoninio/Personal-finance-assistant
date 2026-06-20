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
Visit `http://localhost:3000` for the dashboard, or any of: `/transactions`, `/accounts`, `/subscriptions`, `/budgets`, `/assistant`, `/settings`.

### Enabling the chat assistant and bank linking

Two features need credentials you provide yourself — copy `backend/.env.example` to `backend/.env` and fill in:

```
OPENAI_API_KEY=...        # https://platform.openai.com/api-keys — powers the chat assistant
PLAID_CLIENT_ID=...       # https://dashboard.plaid.com/signup — free Sandbox keys, instant
PLAID_SECRET=...          # same dashboard, Team Settings -> Keys -> Sandbox secret
PLAID_ENV=sandbox
FERNET_KEY=...            # generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Restart the backend after editing `.env`. Without these, the app still runs fully — `/assistant` and `/accounts` show a clear "not configured" message instead of crashing — check `/settings` for live status of both integrations.

Bank linking uses **Plaid Sandbox** (fake test institutions, e.g. "Platypus Bank" with username `user_good` / password `pass_good`), not your real bank — this is the standard way fintech portfolio projects demonstrate bank connectivity without a production-access review process.

## Current state

- [x] FastAPI backend (SQLite/SQLAlchemy) with transactions, insights, subscriptions, budgets endpoints, ported from the legacy app's analytics logic.
- [x] Next.js frontend: Dashboard, Accounts, Transactions, Subscriptions, Budgets, Assistant, Settings — all wired to real backend data, no placeholder pages.
- [x] Plaid Sandbox bank linking (Link flow, cursor-based `/transactions/sync`, encrypted access-token storage). Manual sync trigger for now — webhook-driven sync needs a public HTTPS endpoint, noted as follow-up.
- [x] LangGraph-based chat assistant (`/assistant`) with tool-calling access to real spending/subscription/budget data — grounded answers, not a generic chatbot.
- [ ] Statement upload (PDF/CSV/image) on the new stack
- [ ] Postgres + Alembic migrations, deployment (Vercel + Railway/Render)
- [ ] Scheduled/proactive agent workflows (digests, anomaly detection, budget rebalancing with approval) — chat is reactive only so far

See the project plan for the full design and rationale behind these choices (why LangGraph over CrewAI, why Plaid over Teller, why SQL over a vector store, etc.).

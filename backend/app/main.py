from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import (
    accounts,
    agent,
    budgets,
    config_status,
    health,
    insights,
    plaid,
    subscriptions,
    transactions,
)

app = FastAPI(title="Personal Finance Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(transactions.router)
app.include_router(insights.router)
app.include_router(subscriptions.router)
app.include_router(budgets.router)
app.include_router(config_status.router)
app.include_router(accounts.router)
app.include_router(plaid.router)
app.include_router(agent.router)

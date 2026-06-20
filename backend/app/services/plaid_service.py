"""
Plaid integration: Link token creation, public token exchange, and
cursor-based transaction sync via the official `plaid-python` SDK.

Sign convention reminder (see backend/app/seed.py / insights_service.py):
this app stores debit amounts as NEGATIVE numbers and credit amounts as
POSITIVE numbers (e.g. "SPOTIFY PREMIUM" debit -12.99, "SALARY DEPOSIT"
credit 2500.00). insights_service sums credits raw and abs()'s debits.

Plaid's sign convention is the opposite: for `/transactions/sync`, a
positive `amount` means money left the account (debit/expense) and a
negative `amount` means money was deposited (credit/income). So when
importing a Plaid transaction we flip the sign to match this app's
convention while deriving `type` from Plaid's original sign.
"""
from __future__ import annotations

import plaid
from plaid.api import plaid_api
from plaid.exceptions import ApiException
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Account, Category, Institution, Transaction
from app.services import crypto_service

# Single demo user for tonight — no real auth/multi-user support yet.
DEMO_CLIENT_USER_ID = "demo-user"

# Note: plaid-python dropped the separate "Development" environment in
# newer SDK versions (Plaid retired the Development env in favor of just
# Sandbox + Production) — map anything unrecognized to Sandbox.
_ENV_MAP = {
    "sandbox": plaid.Environment.Sandbox,
    "production": plaid.Environment.Production,
}


class PlaidNotConfigured(RuntimeError):
    """Raised when PLAID_CLIENT_ID / PLAID_SECRET are missing."""


def _require_configured() -> None:
    if not settings.plaid_configured:
        raise PlaidNotConfigured(
            "Plaid is not configured — add PLAID_CLIENT_ID and PLAID_SECRET to backend/.env"
        )


def _get_client() -> plaid_api.PlaidApi:
    _require_configured()
    host = _ENV_MAP.get(settings.plaid_env, plaid.Environment.Sandbox)
    configuration = plaid.Configuration(
        host=host,
        api_key={
            "clientId": settings.plaid_client_id,
            "secret": settings.plaid_secret,
        },
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


def create_link_token() -> str:
    """Create a Plaid Link token for the (single, demo) user to start the Link flow."""
    client = _get_client()
    request = LinkTokenCreateRequest(
        products=[Products("transactions")],
        client_name="Personal Finance Assistant",
        country_codes=[CountryCode("US")],
        language="en",
        user=LinkTokenCreateRequestUser(client_user_id=DEMO_CLIENT_USER_ID),
    )
    response = client.link_token_create(request)
    return response.link_token


def exchange_public_token(public_token: str, db: Session) -> Institution:
    """Exchange a Link `public_token` for a long-lived `access_token`, create the
    Institution row (encrypting the access token at rest), and run an initial sync."""
    client = _get_client()

    exchange_response = client.item_public_token_exchange(
        ItemPublicTokenExchangeRequest(public_token=public_token)
    )
    access_token = exchange_response.access_token
    item_id = exchange_response.item_id

    # institution_name is a placeholder if the item lookup fails — not worth
    # over-investing in tonight per the task brief.
    institution_name = "Linked Bank"
    try:
        from plaid.model.item_get_request import ItemGetRequest

        item_response = client.item_get(ItemGetRequest(access_token=access_token))
        institution_name = item_response.item.institution_name or "Linked Bank"
    except ApiException:
        pass

    institution = Institution(
        plaid_item_id=item_id,
        plaid_access_token_encrypted=crypto_service.encrypt(access_token),
        name=institution_name,
        status="active",
        sync_cursor=None,
    )
    db.add(institution)
    db.commit()
    db.refresh(institution)

    sync_institution(institution, db)
    db.refresh(institution)
    return institution


def _get_or_create_category(db: Session, name: str | None) -> Category | None:
    if not name:
        return None
    category = db.execute(select(Category).where(Category.name == name)).scalar_one_or_none()
    if category is None:
        category = Category(name=name)
        db.add(category)
        db.flush()
    return category


def _category_name_from_plaid(plaid_txn) -> str | None:
    """Prefer Plaid's newer `personal_finance_category.primary`; fall back to the
    legacy `category` list's most specific (last) entry."""
    pfc = getattr(plaid_txn, "personal_finance_category", None)
    if pfc is not None:
        primary = getattr(pfc, "primary", None)
        if primary:
            # Plaid's primary categories are SCREAMING_SNAKE_CASE; make them
            # presentable, e.g. "FOOD_AND_DRINK" -> "Food And Drink".
            return primary.replace("_", " ").title()

    legacy_category = getattr(plaid_txn, "category", None)
    if legacy_category:
        return legacy_category[-1]

    return None


def _upsert_account(db: Session, institution: Institution, plaid_account) -> Account:
    account = db.execute(
        select(Account).where(Account.plaid_account_id == plaid_account.account_id)
    ).scalar_one_or_none()

    balances = getattr(plaid_account, "balances", None)
    current_balance = getattr(balances, "current", None) if balances else None
    available_balance = getattr(balances, "available", None) if balances else None

    if account is None:
        account = Account(
            institution_id=institution.id,
            plaid_account_id=plaid_account.account_id,
            name=plaid_account.name,
            type=str(getattr(plaid_account, "subtype", None) or getattr(plaid_account, "type", None) or ""),
            mask=plaid_account.mask,
            current_balance=current_balance,
            available_balance=available_balance,
        )
        db.add(account)
    else:
        account.name = plaid_account.name
        account.mask = plaid_account.mask
        account.current_balance = current_balance
        account.available_balance = available_balance

    db.flush()
    return account


def sync_institution(institution: Institution, db: Session) -> dict:
    """Cursor-based sync via `/transactions/sync` (NOT the deprecated
    `/transactions/get`). Upserts accounts and transactions, and advances
    `institution.sync_cursor` so the next call only pulls the delta.

    Note: tonight this is only triggered manually (on initial link, and via
    POST /plaid/sync/{institution_id}) rather than by a Plaid webhook — a
    real webhook needs a publicly reachable HTTPS endpoint, which isn't
    practical for a localhost demo without something like ngrok.
    """
    client = _get_client()
    access_token = crypto_service.decrypt(institution.plaid_access_token_encrypted)

    added_count = 0
    modified_count = 0
    removed_count = 0
    accounts_by_id: dict[str, Account] = {}

    cursor = institution.sync_cursor
    has_more = True

    while has_more:
        request = TransactionsSyncRequest(access_token=access_token)
        if cursor:
            request.cursor = cursor

        response = client.transactions_sync(request)

        for plaid_account in response.accounts:
            account = _upsert_account(db, institution, plaid_account)
            accounts_by_id[plaid_account.account_id] = account

        for plaid_txn in response.added:
            _upsert_transaction(db, accounts_by_id, plaid_txn)
            added_count += 1

        for plaid_txn in response.modified:
            _upsert_transaction(db, accounts_by_id, plaid_txn)
            modified_count += 1

        for removed in response.removed:
            existing = db.execute(
                select(Transaction).where(Transaction.plaid_transaction_id == removed.transaction_id)
            ).scalar_one_or_none()
            if existing is not None:
                db.delete(existing)
                removed_count += 1

        cursor = response.next_cursor
        has_more = response.has_more

    institution.sync_cursor = cursor
    db.commit()

    return {
        "added": added_count,
        "modified": modified_count,
        "removed": removed_count,
    }


def _upsert_transaction(db: Session, accounts_by_id: dict[str, Account], plaid_txn) -> None:
    account = accounts_by_id.get(plaid_txn.account_id)
    if account is None:
        account = db.execute(
            select(Account).where(Account.plaid_account_id == plaid_txn.account_id)
        ).scalar_one_or_none()

    plaid_amount = float(plaid_txn.amount)
    # Plaid: positive = money out (debit), negative = money in (credit).
    # This app: debits stored negative, credits stored positive — so flip sign.
    is_debit = plaid_amount > 0
    stored_amount = -plaid_amount

    category_name = _category_name_from_plaid(plaid_txn)
    category = _get_or_create_category(db, category_name)

    existing = db.execute(
        select(Transaction).where(Transaction.plaid_transaction_id == plaid_txn.transaction_id)
    ).scalar_one_or_none()

    if existing is None:
        existing = Transaction(plaid_transaction_id=plaid_txn.transaction_id, source="plaid")
        db.add(existing)

    existing.date = plaid_txn.date
    existing.amount = stored_amount
    existing.description = plaid_txn.name
    existing.type = "debit" if is_debit else "credit"
    existing.category_id = category.id if category else None
    existing.account_id = account.id if account else None
    existing.pending = bool(plaid_txn.pending)
    existing.source = "plaid"

    db.flush()

from datetime import date as date_type
from datetime import datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Category(Base):
    """Minimal category stub: just enough to label a transaction."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category")


class Merchant(Base):
    """Minimal merchant stub for future enrichment; not populated by the seed script yet."""

    __tablename__ = "merchants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="merchant")


class Institution(Base):
    """A linked Plaid Item (one bank login can expose multiple accounts)."""

    __tablename__ = "institutions"

    id: Mapped[int] = mapped_column(primary_key=True)
    plaid_item_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    plaid_access_token_encrypted: Mapped[str] = mapped_column(String(500), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    sync_cursor: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    accounts: Mapped[list["Account"]] = relationship(back_populates="institution")


class Account(Base):
    """One bank account belonging to a linked Institution."""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id"), nullable=False)
    plaid_account_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mask: Mapped[str | None] = mapped_column(String(10), nullable=True)
    current_balance: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    available_balance: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    institution: Mapped[Institution] = relationship(back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # "debit" | "credit"

    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    merchant_id: Mapped[int | None] = mapped_column(ForeignKey("merchants.id"), nullable=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)

    source: Mapped[str] = mapped_column(String(50), nullable=False, default="manual_csv")
    plaid_transaction_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    pending: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    category: Mapped[Category | None] = relationship(back_populates="transactions")
    merchant: Mapped[Merchant | None] = relationship(back_populates="transactions")
    account: Mapped[Account | None] = relationship(back_populates="transactions")

    @property
    def category_name(self) -> str | None:
        return self.category.name if self.category else None


class Subscription(Base):
    """A recurring charge detected by the heuristic in subscription_service.py."""

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    merchant_name: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    cadence: Mapped[str] = mapped_column(String(20), default="monthly")
    first_seen_date: Mapped[date_type] = mapped_column(Date, nullable=False)
    last_seen_date: Mapped[date_type] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active|cancelled_flagged|dismissed
    detected_by: Mapped[str] = mapped_column(String(20), default="heuristic")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Budget(Base):
    """A monthly spending limit for a category."""

    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    period: Mapped[str] = mapped_column(String(20), default="monthly")
    amount_limit: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    effective_from: Mapped[date_type] = mapped_column(Date, nullable=False)

    category: Mapped[Category] = relationship()

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


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # "debit" | "credit"

    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    merchant_id: Mapped[int | None] = mapped_column(ForeignKey("merchants.id"), nullable=True)

    source: Mapped[str] = mapped_column(String(50), nullable=False, default="manual_csv")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    category: Mapped[Category | None] = relationship(back_populates="transactions")
    merchant: Mapped[Merchant | None] = relationship(back_populates="transactions")

    @property
    def category_name(self) -> str | None:
        return self.category.name if self.category else None

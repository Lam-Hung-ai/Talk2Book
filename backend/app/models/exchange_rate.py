# app/models/exchange_rates.py
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Column, Numeric
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from app.models.currency import Currency


class ExchangeRate(SQLModel, table=True):
    __tablename__ = "exchange_rate"  # type: ignore

    __table_args__ = (
        UniqueConstraint(
            "rate_date", "base", "quote", name="uq_exrates_date_base_quote"
        ),
        CheckConstraint("base <> quote", name="check_exrates_base_neq_quote"),
        CheckConstraint("rate > 0", name="check_exrates_rate_positive"),
    )

    rate_date: date = Field(primary_key=True, nullable=False)

    base: str = Field(
        primary_key=True,
        nullable=False,
        foreign_key="currency.code",
        max_length=3,
        ondelete="RESTRICT",
    )

    quote: str = Field(
        primary_key=True,
        nullable=False,
        foreign_key="currency.code",
        max_length=3,
        ondelete="RESTRICT",
    )

    rate: Decimal = Field(sa_column=Column(Numeric(18, 8), nullable=False))

    # Relationships
    base_currency: "Currency" = Relationship(
        back_populates="base_exchange_rates",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRate.base]"},
    )
    quote_currency: "Currency" = Relationship(
        back_populates="quote_exchange_rates",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRate.quote]"},
    )

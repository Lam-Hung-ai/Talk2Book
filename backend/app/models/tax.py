# app/models/taxes.py
from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Column, Numeric
from sqlmodel import DateTime, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.currency import Currency


class Tax(SQLModel, table=True):
    __tablename__ = "tax"  # type: ignore

    __table_args__ = (
        CheckConstraint(
            "(rate IS NOT NULL AND amount IS NULL) OR (rate IS NULL AND amount IS NOT NULL)",
            name="check_tax_rate_or_amount",
        ),
        CheckConstraint(
            "rate IS NULL OR (rate >= 0 AND rate <= 1)", name="check_tax_rate_range"
        ),
        CheckConstraint(
            "amount IS NULL OR amount >= 0", name="check_tax_amount_positive"
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scope: str = Field(nullable=False, max_length=20)
    name: str = Field(nullable=False)
    rate: Decimal | None = Field(default=None, sa_column=Column(Numeric(6, 3)))
    amount: Decimal | None = Field(default=None, sa_column=Column(Numeric(12, 2)))
    currency_code: str | None = Field(
        default=None, foreign_key="currency.code", max_length=3, ondelete="RESTRICT"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    currency: Optional["Currency"] = Relationship(back_populates="taxes")

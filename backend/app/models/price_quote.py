# app/models/price_quotes.py
from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Column, Index, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import DateTime, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.currency import Currency
    from app.models.user import User


class PriceQuote(SQLModel, table=True):
    __tablename__ = "price_quote"  # type: ignore

    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="check_price_quotes_amount_positive"),
        # Lưu ý: CheckConstraint với now() có thể gây warning trong một số tool migration
        # nhưng vẫn hợp lệ về mặt SQL.
        CheckConstraint(
            "expires_at > (now() - interval '1 minute')",
            name="check_price_quotes_expiry",
        ),
        Index("idx_price_quotes_expiry", "expires_at"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    user_id: UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )

    vertical: str = Field(nullable=False, max_length=20)
    payload: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))

    currency_code: str = Field(
        nullable=False, foreign_key="currency.code", max_length=3, ondelete="RESTRICT"
    )

    total_amount: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))

    expires_at: datetime = Field(nullable=False, sa_type=DateTime(timezone=True))

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="price_quotes")
    currency: "Currency" = Relationship(back_populates="price_quotes")
    bookings: list["Booking"] = Relationship(back_populates="quote")

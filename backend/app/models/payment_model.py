from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import PaymentStatus

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.currency import Currency


class Payment(SQLModel, table=True):
    __tablename__ = "payment"  # type: ignore
    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_payment_amount"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    booking_id: UUID = Field(
        foreign_key="booking.id", nullable=False, ondelete="CASCADE"
    )
    provider: str = Field(nullable=False)
    amount: Decimal = Field(max_digits=12, decimal_places=2, nullable=False)
    currency_code: str = Field(
        max_length=3,
        foreign_key="currency.code",
        nullable=False,
        ondelete="RESTRICT"
    )
    status: PaymentStatus = Field(nullable=False)
    idempotency_key: str | None = Field(default=None, unique=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    booking: "Booking" = Relationship(back_populates="payments")
    currency: "Currency" = Relationship(back_populates="payments")

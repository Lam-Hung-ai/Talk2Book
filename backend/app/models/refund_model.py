from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import RefundStatus

if TYPE_CHECKING:
    from app.models.booking import Booking


class Refund(SQLModel, table=True):
    __tablename__ = "refund"  # type: ignore
    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_refund_amount"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    booking_id: UUID = Field(
        foreign_key="booking.id", nullable=False, ondelete="CASCADE"
    )
    amount: Decimal = Field(max_digits=12, decimal_places=2, nullable=False)
    reason: str | None = Field(default=None)
    status: RefundStatus = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    booking: "Booking" = Relationship(back_populates="refunds")

from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Column, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.ticket import Ticket


class BookingItem(SQLModel, table=True):
    __tablename__ = "booking_item"  # type: ignore
    __table_args__ = (
        CheckConstraint("price_amount >= 0", name="chk_item_price_amount"),
        Index("idx_booking_item_booking", "booking_id"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    booking_id: UUID = Field(
        nullable=False, foreign_key="booking.id", ondelete="CASCADE"
    )
    vertical: str = Field(max_length=20, nullable=False)
    supplier_ref: str | None = Field(default=None)
    details: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    price_amount: Decimal = Field(max_digits=12, decimal_places=2, nullable=False)

    # Relationships
    booking: "Booking" = Relationship(back_populates="items")
    tickets: list["Ticket"] = Relationship(back_populates="booking_item")

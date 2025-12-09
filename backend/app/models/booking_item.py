from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint
from sqlmodel import JSON, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.booking import Booking

class BookingItem(SQLModel, table=True):
    __tablename__ = "booking_item" # type: ignore

    __table_args__ = (
        CheckConstraint("price_amount >= 0", name="chk_item_price_amount"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    booking_id: UUID = Field(
        nullable=False, foreign_key="booking.id", ondelete="CASCADE", index=True
    )

    vertical: str = Field(max_length=20, nullable=False)
    supplier_ref: str | None = Field(default=None)
    details: dict[str, Any] = Field(default={}, sa_type=JSON, nullable=False)

    price_amount: Decimal = Field(default=0, max_digits=12, decimal_places=2, nullable=False)

    # Relationship
    booking: "Booking" = Relationship(back_populates="items")

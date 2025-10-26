from typing import TYPE_CHECKING, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, JSON

if TYPE_CHECKING:
    from .bookings import Booking
    from .products import Product
    from .time_slots import TimeSlot


class BookingItem(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    booking_id: UUID = Field(nullable=False, foreign_key="booking.id", ondelete="CASCADE")
    product_id: UUID | None = Field(default=None, foreign_key="product.id")
    time_slot_id: UUID | None = Field(default=None, foreign_key="time_slot.id")
    quantity: int = Field(default=1, nullable=False)
    unit_price: float = Field(nullable=False)
    currency_code: str | None = Field(default=None, foreign_key="currency.code", max_length=3)
    total_amount: float = Field(nullable=False)
    snapshot: Any | None = Field(default=None, sa_column=Column(JSON), description="Snapshot of product/time_slot & pricing")
    created_at: datetime | None = Field(default=datetime.now())

    booking: "Booking" = Relationship(back_populates="items")

from typing import Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, JSON

class BookingItem(SQLModel, table=True):
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    booking_id: UUID = Field(nullable=False, foreign_key="booking.id", ondelete="CASCADE")
    product_id: Optional[UUID] = Field(default=None, foreign_key="product.id")
    time_slot_id: Optional[UUID] = Field(default=None, foreign_key="time_slot.id")
    quantity: int = Field(default=1, nullable=False)
    unit_price: float = Field(nullable=False)
    currency_code: Optional[str] = Field(default=None, foreign_key="currency.code", max_length=3)
    total_amount: float = Field(nullable=False)
    snapshot: Optional[Any] = Field(default=None, sa_column=Column(JSON), description="Snapshot of product/time_slot & pricing")
    created_at: Optional[datetime] = Field(default=datetime.now())

    booking: "Booking" = Relationship(back_populates="items")

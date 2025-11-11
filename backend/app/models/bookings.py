from typing import TYPE_CHECKING, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, JSON

if TYPE_CHECKING:
    from .user import User
    from .price_quotes import PriceQuote
    from .booking_items import BookingItem


class BookingStatus(str):
    created = "created"
    paid = "paid"
    canceled = "canceled"
    failed = "failed"
    refunded = "refunded"


class Booking(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID | None = Field(default=None, foreign_key="user.id")
    status: str | None = Field(default=BookingStatus.created)
    created_at: datetime | None = Field(default=datetime.now())
    updated_at: datetime | None = Field(default=datetime.now())
    total_amount: float | None = Field(default=0.0)
    currency_code: str | None = Field(
        default=None, foreign_key="currency.code", max_length=3
    )
    quote_id: UUID | None = Field(default=None, foreign_key="pricequote.id")
    payment_method: str | None = Field(default=None)
    paid_at: datetime | None = Field(default=None)
    meta: Any | None = Field(default=None, sa_column=Column(JSON))

    items: List["BookingItem"] = Relationship(back_populates="booking")

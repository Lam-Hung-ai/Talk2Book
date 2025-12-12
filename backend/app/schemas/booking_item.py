from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class BookingItemBase(BaseModel):
    booking_id: UUID
    vertical: str = Field(max_length=20)
    supplier_ref: str | None = None
    details: dict[str, Any]
    price_amount: Decimal = Field(max_digits=12, decimal_places=2)


class BookingItemCreate(BookingItemBase):
    pass


class BookingItemUpdate(BaseModel):
    vertical: str | None = Field(default=None, max_length=20)
    supplier_ref: str | None = None
    details: dict[str, Any] | None = None
    price_amount: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)


class BookingItemRead(BookingItemBase):
    id: UUID

    class Config:
        from_attributes = True


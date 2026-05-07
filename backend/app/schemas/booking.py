from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import BookingState


class BookingBase(BaseModel):
    user_id: str | None = None
    state: BookingState
    currency_code: str = Field(max_length=3)
    total_amount: Decimal = Field(max_digits=12, decimal_places=2)
    quote_id: UUID | None = None
    coupon_id: UUID | None = None


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    user_id: str | None = None
    state: BookingState | None = None
    currency_code: str | None = Field(default=None, max_length=3)
    total_amount: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)
    quote_id: UUID | None = None
    coupon_id: UUID | None = None


class BookingRead(BookingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

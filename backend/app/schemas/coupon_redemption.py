from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CouponRedemptionBase(BaseModel):
    coupon_id: UUID
    user_id: str
    booking_id: UUID
    discount_amount: Decimal = Field(gt=0)
    currency_code: str = Field(max_length=3)


class CouponRedemptionCreate(CouponRedemptionBase):
    pass


class CouponRedemptionUpdate(BaseModel):
    discount_amount: Decimal | None = Field(default=None, gt=0)
    currency_code: str | None = Field(default=None, max_length=3)


class CouponRedemptionRead(CouponRedemptionBase):
    id: UUID
    redeemed_at: datetime

    class Config:
        from_attributes = True

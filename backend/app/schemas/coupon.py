from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import DiscountType


class CouponBase(BaseModel):
    code: str = Field(min_length=1)
    discount_type: DiscountType
    discount_value: Decimal = Field(gt=0)
    currency_code: str | None = Field(default=None, max_length=3)
    min_order_amount: Decimal | None = Field(default=None, ge=0)
    max_discount_amount: Decimal | None = Field(default=None, ge=0)
    max_uses_total: int | None = Field(default=None, ge=0)
    max_uses_per_user: int | None = Field(default=None, ge=0)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    is_active: bool = True


class CouponCreate(CouponBase):
    pass


class CouponUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1)
    discount_type: DiscountType | None = None
    discount_value: Decimal | None = Field(default=None, gt=0)
    currency_code: str | None = Field(default=None, max_length=3)
    min_order_amount: Decimal | None = Field(default=None, ge=0)
    max_discount_amount: Decimal | None = Field(default=None, ge=0)
    max_uses_total: int | None = Field(default=None, ge=0)
    max_uses_per_user: int | None = Field(default=None, ge=0)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    is_active: bool | None = None


class CouponRead(CouponBase):
    id: UUID
    current_uses: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


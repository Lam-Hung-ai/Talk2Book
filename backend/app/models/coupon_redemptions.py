from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, SQLModel

class CouponRedemption(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    coupon_id: UUID = Field(nullable=False, foreign_key="coupon.id", ondelete="RESTRICT")
    user_id: Optional[UUID] = Field(default=None, foreign_key="user.id", ondelete="SET NULL")
    booking_id: Optional[UUID] = Field(default=None, foreign_key="booking.id", ondelete="SET NULL")
    redeemed_at: Optional[datetime] = Field(default=datetime.now())
    saved_amount: Optional[float] = Field(default=None)
    currency_code: Optional[str] = Field(default=None, foreign_key="currency.code", max_length=3)

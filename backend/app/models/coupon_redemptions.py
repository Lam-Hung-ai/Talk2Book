from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    pass


class CouponRedemption(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    coupon_id: UUID = Field(
        nullable=False, foreign_key="coupon.id", ondelete="RESTRICT"
    )
    user_id: UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    booking_id: UUID | None = Field(
        default=None, foreign_key="booking.id", ondelete="SET NULL"
    )
    redeemed_at: datetime | None = Field(default=datetime.now())
    saved_amount: float | None = Field(default=None)
    currency_code: str | None = Field(
        default=None, foreign_key="currency.code", max_length=3
    )

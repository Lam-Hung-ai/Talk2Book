from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint
from sqlmodel import DateTime, Field, Relationship, SQLModel

from app.models.enums import DiscountType

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.currency import Currency

class Coupon(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint(
            "starts_at IS NULL OR ends_at IS NULL OR starts_at < ends_at",
            name="chk_coupon_window"
        ),
        CheckConstraint(
            """
            (discount_type = 'percent' AND discount_value >= 0 AND discount_value <= 100 AND currency_code IS NULL)
            OR
            (discount_type = 'amount'  AND discount_value >= 0 AND currency_code IS NOT NULL)
            """,
            name="chk_coupon_value"
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    code: str = Field(unique=True, nullable=False, index=True)
    discount_type: DiscountType = Field(nullable=False)

    discount_value: Decimal = Field(default=0, max_digits=12, decimal_places=2, nullable=False)

    currency_code: str = Field(nullable=False, max_length=3, foreign_key="currency.code", ondelete="RESTRICT")

    starts_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    ends_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))

    # Relationship
    bookings: list["Booking"] = Relationship(back_populates="coupon")

    currency: Optional["Currency"] = Relationship(back_populates="coupons")

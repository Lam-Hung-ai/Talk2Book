from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Column, func
from sqlalchemy import DateTime as SA_DateTime
from sqlmodel import DateTime, Field, Relationship, SQLModel

from app.models.enums import DiscountType

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.coupon_redemption import CouponRedemption
    from app.models.currency import Currency


class Coupon(SQLModel, table=True):
    __tablename__ = "coupon"  # type: ignore
    __table_args__ = (
        CheckConstraint(
            "starts_at IS NULL OR ends_at IS NULL OR starts_at < ends_at",
            name="chk_coupon_window"
        ),
        CheckConstraint(
            "current_uses >= 0 AND (max_uses_total IS NULL OR current_uses <= max_uses_total)",
            name="chk_coupon_usage_limit"
        ),
        CheckConstraint(
            """
            (discount_type = 'percent' AND discount_value >= 0 AND discount_value <= 100)
            OR
            (discount_type = 'amount'  AND discount_value >= 0 AND currency_code IS NOT NULL)
            """,
            name="chk_coupon_logic"
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    code: str = Field(unique=True, nullable=False)
    discount_type: DiscountType = Field(nullable=False)
    discount_value: Decimal = Field(max_digits=12, decimal_places=2, nullable=False)
    currency_code: str | None = Field(
        default=None, max_length=3, foreign_key="currency.code", ondelete="RESTRICT"
    )
    min_order_amount: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)
    max_discount_amount: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)
    max_uses_total: int | None = Field(default=None)
    max_uses_per_user: int | None = Field(default=None)
    current_uses: int = Field(default=0, nullable=False)
    starts_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    ends_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            SA_DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now()
        ),
    )

    # Relationships
    bookings: list["Booking"] = Relationship(back_populates="coupon")
    redemptions: list["CouponRedemption"] = Relationship(back_populates="coupon")
    currency: Optional["Currency"] = Relationship(back_populates="coupons")

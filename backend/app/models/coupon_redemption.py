from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from sqlmodel import DateTime, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.coupon import Coupon
    from app.models.currency import Currency
    from app.models.user import User


class CouponRedemption(SQLModel, table=True):
    __tablename__ = "coupon_redemption"  # type: ignore
    __table_args__ = (
        UniqueConstraint("booking_id", "coupon_id", name="uq_redemption_booking"),
        CheckConstraint("discount_amount > 0", name="chk_redemption_amount"),
        Index("idx_redemption_user_coupon", "user_id", "coupon_id"),
        Index("idx_redemption_coupon", "coupon_id"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    coupon_id: UUID = Field(
        nullable=False, foreign_key="coupon.id", ondelete="RESTRICT"
    )
    user_id: str = Field(nullable=False, foreign_key="user.id", ondelete="CASCADE")
    booking_id: UUID = Field(
        nullable=False, foreign_key="booking.id", ondelete="CASCADE"
    )
    discount_amount: Decimal = Field(max_digits=12, decimal_places=2, nullable=False)
    currency_code: str = Field(
        nullable=False, max_length=3, foreign_key="currency.code", ondelete="RESTRICT"
    )
    redeemed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    coupon: "Coupon" = Relationship(back_populates="redemptions")
    user: "User" = Relationship(back_populates="coupon_redemptions")
    booking: "Booking" = Relationship(back_populates="coupon_redemption")
    currency: "Currency" = Relationship(back_populates="coupon_redemptions")

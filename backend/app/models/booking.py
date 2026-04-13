from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Column, func
from sqlalchemy import DateTime as SA_DateTime
from sqlmodel import DateTime, Field, Relationship, SQLModel

from app.models.enums import BookingState

if TYPE_CHECKING:
    from app.models.booking_audit_log import BookingAuditLog
    from app.models.booking_item import BookingItem
    from app.models.coupon import Coupon
    from app.models.coupon_redemption import CouponRedemption
    from app.models.currency import Currency
    from app.models.passenger import Passenger
    from app.models.payment import Payment
    from app.models.price_quote import PriceQuote
    from app.models.user import User


class Booking(SQLModel, table=True):
    __tablename__ = "booking"  # type: ignore
    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="chk_booking_total_amount"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    state: BookingState = Field(nullable=False)
    currency_code: str = Field(
        nullable=False, max_length=3, foreign_key="currency.code", ondelete="RESTRICT"
    )
    total_amount: Decimal = Field(max_digits=12, decimal_places=2, nullable=False)
    quote_id: UUID | None = Field(
        default=None, foreign_key="price_quote.id", ondelete="SET NULL"
    )
    coupon_id: UUID | None = Field(
        default=None, foreign_key="coupon.id", ondelete="SET NULL"
    )
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
            onupdate=func.now(),
        ),
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="bookings")
    coupon: Optional["Coupon"] = Relationship(back_populates="bookings")
    coupon_redemption: Optional["CouponRedemption"] = Relationship(
        back_populates="booking"
    )
    items: list["BookingItem"] = Relationship(back_populates="booking")
    passengers: list["Passenger"] = Relationship(back_populates="booking")
    currency: Optional["Currency"] = Relationship(back_populates="bookings")
    quote: Optional["PriceQuote"] = Relationship(back_populates="bookings")
    audit_logs: list["BookingAuditLog"] = Relationship(back_populates="booking")
    payments: list["Payment"] = Relationship(back_populates="booking")

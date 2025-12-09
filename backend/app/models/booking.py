from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint
from sqlalchemy import DateTime as SA_DateTime
from sqlmodel import DateTime, Field, Relationship, SQLModel

from app.models.enums import BookingState

if TYPE_CHECKING:
    from app.models.booking_item import BookingItem
    from app.models.coupon import Coupon

    # from app.models.price_quote import PriceQuote # Nếu có
    from app.models.currency import Currency
    from app.models.user import User

class Booking(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="chk_booking_total_amount"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    user_id: UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    # quote_id: UUID | None = Field(
    #     default=None, foreign_key="price_quote.id", ondelete="SET NULL"
    # )
    coupon_id: UUID | None = Field(
        default=None, foreign_key="coupon.id", ondelete="SET NULL"
    )
    currency_code: str = Field(
        nullable=False, max_length=3, foreign_key="currency.code", ondelete="RESTRICT"
    )

    state: BookingState = Field(nullable=False)
    total_amount: Decimal = Field(default=0, max_digits=12, decimal_places=2, nullable=False)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=SA_DateTime(timezone=True),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="bookings")
    coupon: Optional["Coupon"] = Relationship(back_populates="bookings")
    items: list["BookingItem"] = Relationship(back_populates="booking")
    currency: Optional["Currency"] = Relationship(back_populates="bookings")
    # price_quote: Optional["PriceQuote"] = Relationship() # Nếu có

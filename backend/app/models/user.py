# app/models/user.py — Better Auth core user (aligned with frontend/db/schema.ts)
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column
from sqlalchemy import DateTime as SA_DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.user_role import UserRole

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.booking import Booking
    from app.models.booking_audit_log import BookingAuditLog
    from app.models.coupon_redemption import CouponRedemption
    from app.models.price_quote import PriceQuote
    from app.models.review import Review
    from app.models.role import Role
    from app.models.session import Session
    from app.models.user_profile import UserProfile


class User(SQLModel, table=True):
    __tablename__ = "user"  # type: ignore

    id: str = Field(primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True, index=True)
    email_verified: bool = Field(default=False, nullable=False)
    image: str | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(SA_DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(SA_DateTime(timezone=True), nullable=False),
    )

    sessions: list["Session"] = Relationship(back_populates="user")
    accounts: list["Account"] = Relationship(back_populates="user")
    user_profile: Optional["UserProfile"] = Relationship(back_populates="user")
    roles: list["Role"] = Relationship(back_populates="users", link_model=UserRole)
    bookings: list["Booking"] = Relationship(back_populates="user")
    price_quotes: list["PriceQuote"] = Relationship(back_populates="user")
    booking_audit_logs: list["BookingAuditLog"] = Relationship(back_populates="actor")
    coupon_redemptions: list["CouponRedemption"] = Relationship(back_populates="user")
    reviews: list["Review"] = Relationship(back_populates="user")

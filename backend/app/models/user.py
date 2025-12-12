# app/models/user.py
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import DateTime, Field, Relationship, SQLModel

from app.models.enums import UserStatus
from app.models.user_role import UserRole

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.booking_audit_log import BookingAuditLog
    from app.models.coupon_redemption import CouponRedemption
    from app.models.price_quote import PriceQuote
    from app.models.refresh_token import RefreshToken
    from app.models.review_model import Review
    from app.models.role import Role
    from app.models.support_ticket_model import SupportTicket
    from app.models.user_profile import UserProfile


class User(SQLModel, table=True):
    __tablename__ = "user"  # type: ignore
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, nullable=False, index=True)
    phone: str = Field(unique=True, nullable=False, max_length=32, index=True)
    password_hash: str = Field(nullable=False)
    status: UserStatus = Field(default=UserStatus.active, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    user_profile: Optional["UserProfile"] = Relationship(back_populates="user")
    roles: list["Role"] = Relationship(back_populates="users", link_model=UserRole)
    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user")
    bookings: list["Booking"] = Relationship(back_populates="user")
    price_quotes: list["PriceQuote"] = Relationship(back_populates="user")
    booking_audit_logs: list["BookingAuditLog"] = Relationship(back_populates="actor")
    coupon_redemptions: list["CouponRedemption"] = Relationship(back_populates="user")
    reviews: list["Review"] = Relationship(back_populates="user")
    support_tickets: list["SupportTicket"] = Relationship(back_populates="user")

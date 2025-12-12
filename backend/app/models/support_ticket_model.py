from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, func
from sqlalchemy import DateTime as SA_DateTime
from sqlmodel import DateTime, Field, Relationship, SQLModel

from app.models.enums import SupportStatus

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.user import User


class SupportTicket(SQLModel, table=True):
    __tablename__ = "support_ticket"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    booking_id: UUID | None = Field(
        default=None,
        foreign_key="booking.id",
        ondelete="SET NULL"
    )
    subject: str = Field(nullable=False)
    status: SupportStatus = Field(nullable=False)
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
    user: "User" = Relationship(back_populates="support_tickets")
    booking: Optional["Booking"] = Relationship(back_populates="support_tickets")

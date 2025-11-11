from typing import TYPE_CHECKING, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON

if TYPE_CHECKING:
    from .bookings import Booking
    from .user import User


class ActorType(str):
    system = "system"
    user = "user"


class BookingAuditLog(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    booking_id: UUID = Field(
        nullable=False, foreign_key="booking.id", ondelete="CASCADE"
    )
    actor_type: str | None = Field(default=ActorType.system)
    actor_id: UUID | None = Field(default=None, foreign_key="user.id")
    action: str = Field(nullable=False)
    from_state: str | None = Field(default=None)
    to_state: str | None = Field(default=None)
    created_at: datetime | None = Field(default=datetime.now())
    meta: Any | None = Field(default=None, sa_column=Column(JSON))

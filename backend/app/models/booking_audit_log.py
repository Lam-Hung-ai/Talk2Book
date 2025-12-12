from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import DateTime, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.user import User


class BookingAuditLog(SQLModel, table=True):
    __tablename__ = "booking_audit_log"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    booking_id: UUID = Field(
        nullable=False, foreign_key="booking.id", ondelete="CASCADE"
    )
    actor_type: str | None = Field(default=None)
    actor_id: UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    action: str = Field(nullable=False)
    from_state: str | None = Field(default=None)
    to_state: str | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    meta: dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB))

    # Relationships
    booking: "Booking" = Relationship(back_populates="audit_logs")
    actor: Optional["User"] = Relationship(back_populates="booking_audit_logs")

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import TicketType

if TYPE_CHECKING:
    from app.models.booking_item import BookingItem


class Ticket(SQLModel, table=True):
    __tablename__ = "ticket"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    item_id: UUID = Field(
        nullable=False, foreign_key="booking_item.id", ondelete="CASCADE"
    )
    type: TicketType = Field(nullable=False)
    code: str = Field(unique=True, nullable=False)
    issued_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    booking_item: "BookingItem" = Relationship(back_populates="tickets")

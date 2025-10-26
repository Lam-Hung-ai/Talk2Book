from typing import TYPE_CHECKING, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON

if TYPE_CHECKING:
    from .booking_items import BookingItem


class TicketStatus(str):
    issued = "issued"
    cancelled = "cancelled"
    used = "used"


class Ticket(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    code: str = Field(nullable=False, unique=True, max_length=128)
    booking_item_id: UUID | None = Field(default=None, foreign_key="bookingitem.id")
    issued_at: datetime | None = Field(default=datetime.now())
    valid_from: datetime | None = Field(default=None)
    valid_to: datetime | None = Field(default=None)
    status: str | None = Field(default=TicketStatus.issued)
    data: Any | None = Field(default=None, sa_column=Column(JSON))

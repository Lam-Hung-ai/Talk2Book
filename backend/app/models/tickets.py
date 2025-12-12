from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    pass


class TicketStatus(str):
    issued = "issued"
    cancelled = "cancelled"
    used = "used"


class Ticket(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    code: str = Field(nullable=False, unique=True, max_length=128)
    booking_item_id: UUID | None = Field(default=None, foreign_key="booking_item.id")
    issued_at: datetime | None = Field(default=datetime.now())
    valid_from: datetime | None = Field(default=None)
    valid_to: datetime | None = Field(default=None)
    status: str | None = Field(default=TicketStatus.issued)
    data: Any | None = Field(default=None, sa_column=Column(JSON))

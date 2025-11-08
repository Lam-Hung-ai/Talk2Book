from typing import Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON

class TicketStatus(str):
    issued = "issued"
    cancelled = "cancelled"
    used = "used"

class Ticket(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    code: str = Field(nullable=False, unique=True, max_length=128)
    booking_item_id: Optional[UUID] = Field(default=None, foreign_key="bookingitem.id")
    issued_at: Optional[datetime] = Field(default=datetime.now())
    valid_from: Optional[datetime] = Field(default=None)
    valid_to: Optional[datetime] = Field(default=None)
    status: Optional[str] = Field(default=TicketStatus.issued)
    data: Optional[Any] = Field(default=None, sa_column=Column(JSON))

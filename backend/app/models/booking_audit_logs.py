from typing import Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON

class ActorType(str):
    system = "system"
    user = "user"

class BookingAuditLog(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    booking_id: UUID = Field(nullable=False, foreign_key="booking.id", ondelete="CASCADE")
    actor_type: Optional[str] = Field(default=ActorType.system)
    actor_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    action: str = Field(nullable=False)
    from_state: Optional[str] = Field(default=None)
    to_state: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default=datetime.now())
    meta: Optional[Any] = Field(default=None, sa_column=Column(JSON))

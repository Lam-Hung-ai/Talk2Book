from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user_model import User

class SupportTicket(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    booking_id: int | None = Field(default=None)
    user_id: UUID = Field(foreign_key="user.id")
    subject: str
    message: str
    status: str = "open"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="support_tickets")

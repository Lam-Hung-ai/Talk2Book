from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.user_model import User

class SupportTicket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    booking_id: Optional[int] = Field(default=None)
    user_id: UUID = Field(foreign_key="user.id")
    subject: str
    message: str
    status: str = "open"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="support_tickets")

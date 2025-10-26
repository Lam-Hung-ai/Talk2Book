from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from uuid import UUID

from database.models.user_model import User

class SupportTicket(SQLModel, table=True):
    __tablename__ = "support_tickets"

    id: Optional[int] = Field(default=None, primary_key=True)
    booking_id: Optional[int] = Field(default=None)
    user_id: UUID = Field(foreign_key="users.id")
    subject: str
    message: str
    status: str = "open"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="support_tickets")

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.payment_model import Payment
    from app.models.review_model import Review
    from app.models.support_ticket_model import SupportTicket

class UserStatus(str, Enum):
    active = "active"
    suspended = "suspended"
    deleted = "deleted"


class User(SQLModel, table=True):
    id: UUID | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    phone: str = Field(unique=True, nullable=False, max_length=32)
    password_hash: str = Field(nullable=False)
    status: UserStatus | None = Field(default=UserStatus.active)
    create_at: datetime | None = Field(default_factory=datetime.now)

    # Relationships
    payments: list["Payment"] = Relationship(back_populates="user")
    reviews: list["Review"] = Relationship(back_populates="user")
    support_tickets: list["SupportTicket"] = Relationship(back_populates="user")

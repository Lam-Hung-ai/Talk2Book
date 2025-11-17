from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID


if TYPE_CHECKING:
    from app.models.user_model import User

class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    service_type: str
    service_id: Optional[int] = Field(default=None)
    rating: int
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="reviews")

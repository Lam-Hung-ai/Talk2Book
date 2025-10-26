from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User

class Gender(str, Enum):
    male = "M"
    femal = "F"
    other = "O"

class UserProfile(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    full_name: str = Field(nullable=False)
    gender: Gender = Field(nullable=False)
    birthday: datetime = Field(nullable=False)
    nationality: str = Field(foreign_key="country.code", nullable=False, ondelete="RESTRICT", max_length=2)
    avartar: str | None
    address: str | None
    updated_at: datetime| None = Field(default=datetime.now())

    user: "User" = Relationship(back_populates="user_profile")
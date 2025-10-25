from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum
from uuid import UUID
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from database.models.user import User

class Gender(str, Enum):
    male = "M"
    femal = "F"
    other = "O"

class UserProfile(SQLModel, table=True):
    id: UUID | None = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    full_name: str = Field(nullable=False)
    gender: Gender = Field(nullable=False)
    bithday: datetime | None = Field(nullable=False)
    nationality: str
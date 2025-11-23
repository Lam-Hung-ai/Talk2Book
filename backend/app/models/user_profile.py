from datetime import UTC, date, datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import DateTime, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class Gender(str, Enum):
    male = "M"
    female = "F"
    other = "O"


class UserProfile(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    full_name: str = Field(nullable=False)
    gender: Gender | None = Field(default=None)
    birthday: date | None = Field(default=None)
    nationality: str | None = Field(
        default=None, foreign_key="country.code", ondelete="RESTRICT", max_length=2
    )
    avatar_url: str | None = None
    address: str | None = None
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    user: "User" = Relationship(back_populates="user_profile")

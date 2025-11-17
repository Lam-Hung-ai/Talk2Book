from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from app.models.user_role import UserRole
from sqlmodel import Field, Relationship, SQLModel, DateTime
from pydantic import EmailStr

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.user_profile import UserProfile
    from app.models.token import RefreshToken


class UserStatus(str, Enum):
    active = "active"
    suspended = "suspended"
    deleted = "deleted"


class User(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, nullable=False, index=True)
    phone: str = Field(unique=True, nullable=False, max_length=32, index=True)
    password_hash: str = Field(nullable=False)
    status: UserStatus | None = Field(default=UserStatus.active, nullable=False)
    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    user_profile: Optional["UserProfile"] = Relationship(back_populates="user")
    roles: list["Role"] = Relationship(back_populates="users", link_model=UserRole)
    sessions: list["RefreshToken"] = Relationship(back_populates="user")

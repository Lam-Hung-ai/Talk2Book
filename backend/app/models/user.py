# app/models/user.py
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import DateTime, Field, Relationship, SQLModel

from app.models.user_role import UserRole

if TYPE_CHECKING:
    from app.models.refresh_token import RefreshToken
    from app.models.role import Role
    from app.models.user_profile import UserProfile


class UserStatus(str, Enum):
    active = "active"
    suspended = "suspended"
    deleted = "deleted"


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, nullable=False, index=True)
    phone: str = Field(unique=True, nullable=False, max_length=32, index=True)
    password_hash: str = Field(nullable=False)
    status: UserStatus = Field(default=UserStatus.active, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    user_profile: Optional["UserProfile"] = Relationship(back_populates="user")
    roles: list["Role"] = Relationship(back_populates="users", link_model=UserRole)
    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user")

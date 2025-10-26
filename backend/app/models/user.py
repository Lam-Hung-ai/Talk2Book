from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from app.models.user_role import UserRole
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.user_profile import UserProfile

class UserStatus(str, Enum):
    active = "active"
    suspended = "suspended"
    deleted = "deleted"

class User(SQLModel, table=True):

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    phone: str = Field(unique=True, nullable=False, max_length=32)
    password_hash: str = Field(nullable=False)
    status: UserStatus | None = Field(default=UserStatus.active)
    create_at: datetime | None = Field(default=datetime.now())

    user_profile: Optional["UserProfile"] = Relationship(back_populates="user")
    roles: list['Role'] = Relationship(back_populates="users", link_model=UserRole)
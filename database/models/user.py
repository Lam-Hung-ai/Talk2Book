from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum
from uuid import UUID

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
    create_at: datetime | None = Field(default=datetime.now())

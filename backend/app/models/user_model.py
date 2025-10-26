from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID


class UserStatus(str, Enum):
    active = "active"
    suspended = "suspended"
    deleted = "deleted"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    phone: str = Field(unique=True, nullable=False, max_length=32)
    password_hash: str = Field(nullable=False)
    status: UserStatus | None = Field(default=UserStatus.active)
    create_at: datetime | None = Field(default_factory=datetime.now)

    # 👇 Không import các model khác, chỉ dùng tên chuỗi để tránh vòng lặp import
    payments: List["Payment"] = Relationship(back_populates="user")
    reviews: List["Review"] = Relationship(back_populates="user")
    support_tickets: List["SupportTicket"] = Relationship(back_populates="user")

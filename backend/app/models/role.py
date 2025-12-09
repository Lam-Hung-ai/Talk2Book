# app/models/role.py
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.models.user_role import UserRole

if TYPE_CHECKING:
    from app.models.user import User


class Role(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    code: str = Field(nullable=False, unique=True)

    users: list["User"] = Relationship(back_populates="roles", link_model=UserRole)

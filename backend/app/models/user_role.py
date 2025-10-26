from uuid import UUID

from sqlmodel import Field, SQLModel


class UserRole(SQLModel, table = True):
    user_id: UUID = Field(nullable=False, primary_key=True, foreign_key="user.id", ondelete="CASCADE")
    role_id: UUID = Field(nullable=False, primary_key=True, foreign_key="role.id", ondelete="CASCADE")
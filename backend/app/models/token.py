from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

class RefreshToken(SQLModel, table=True):
    jti: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key='user.id', nullable=False, ondelete='CASCADE')
    refresh_token: str = Field(nullable=False, index=True)
    revoked: bool | None = Field(default=False, nullable=False)
    expires_at: datetime = Field(default=None, nullable=False)

    user: "User" = Relationship(back_populates='sessions')
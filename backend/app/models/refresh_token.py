from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import DateTime, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class RefreshToken(SQLModel, table=True):
    jti: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    refresh_token: str = Field(nullable=False, index=True)
    revoked: bool | None = Field(default=False, nullable=False)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    user: "User" = Relationship(back_populates="refresh_tokens")

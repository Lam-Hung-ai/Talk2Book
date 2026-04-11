# app/models/session.py — Better Auth (aligned with frontend/db/schema.ts)
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Index
from sqlalchemy import DateTime as SA_DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class Session(SQLModel, table=True):
    __tablename__ = "session"  # type: ignore
    __table_args__ = (Index("session_userId_idx", "user_id"),)

    id: str = Field(primary_key=True)
    expires_at: datetime = Field(
        sa_column=Column(SA_DateTime(timezone=True), nullable=False)
    )
    token: str = Field(unique=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(SA_DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(SA_DateTime(timezone=True), nullable=False),
    )
    ip_address: str | None = None
    user_agent: str | None = None
    user_id: str = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")

    user: "User" = Relationship(back_populates="sessions")

# app/models/account.py — Better Auth (aligned with frontend/db/schema.ts)
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Index
from sqlalchemy import DateTime as SA_DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class Account(SQLModel, table=True):
    __tablename__ = "account"  # type: ignore
    __table_args__ = (Index("account_userId_idx", "user_id"),)

    id: str = Field(primary_key=True)
    account_id: str = Field(nullable=False)
    provider_id: str = Field(nullable=False)
    user_id: str = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    access_token: str | None = None
    refresh_token: str | None = None
    id_token: str | None = None
    access_token_expires_at: datetime | None = Field(
        default=None, sa_column=Column(SA_DateTime(timezone=True), nullable=True)
    )
    refresh_token_expires_at: datetime | None = Field(
        default=None, sa_column=Column(SA_DateTime(timezone=True), nullable=True)
    )
    scope: str | None = None
    password: str | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(SA_DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(SA_DateTime(timezone=True), nullable=False),
    )

    user: "User" = Relationship(back_populates="accounts")

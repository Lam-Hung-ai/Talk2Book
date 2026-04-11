# app/models/verification.py — Better Auth (aligned with frontend/db/schema.ts)
from datetime import UTC, datetime

from sqlalchemy import Column, Index
from sqlalchemy import DateTime as SA_DateTime
from sqlmodel import Field, SQLModel


class Verification(SQLModel, table=True):
    __tablename__ = "verification"  # type: ignore
    __table_args__ = (Index("verification_identifier_idx", "identifier"),)

    id: str = Field(primary_key=True)
    identifier: str = Field(nullable=False)
    value: str = Field(nullable=False)
    expires_at: datetime = Field(
        sa_column=Column(SA_DateTime(timezone=True), nullable=False)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(SA_DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(SA_DateTime(timezone=True), nullable=False),
    )

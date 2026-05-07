from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, UniqueConstraint, func
from sqlalchemy import DateTime as SA_DateTime
from sqlmodel import DateTime, Field, SQLModel


class Category(SQLModel, table=True):
    __tablename__ = "category"  # type: ignore

    __table_args__ = (
        UniqueConstraint("group_name", "value", name="uq_category_group_value"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    group_name: str = Field(nullable=False, index=True)
    value: str = Field(nullable=False)
    description: str | None = Field(default=None)
    sort_order: int = Field(default=0, nullable=False)
    is_active: bool = Field(default=True, nullable=False)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            SA_DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

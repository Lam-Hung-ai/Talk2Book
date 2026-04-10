from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

from app.models.enums import ProductType

if TYPE_CHECKING:
    from app.models.provider import Provider
    from app.models.time_slot import TimeSlot


class Product(SQLModel, table=True):
    __tablename__ = "product"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    provider_id: UUID = Field(
        foreign_key="provider.id", nullable=False, ondelete="RESTRICT"
    )

    type: ProductType = Field(nullable=False)
    title: str = Field(nullable=False)
    description: str = Field(nullable=False)
    image_url: str | None = Field(default=None)
    itinerary: dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    provider: "Provider" = Relationship(back_populates="products")
    time_slots: list["TimeSlot"] = Relationship(back_populates="product")

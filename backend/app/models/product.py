from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import DateTime, Field, Relationship, SQLModel

from app.models.enums import ProductType

if TYPE_CHECKING:
    from app.models.city import City
    from app.models.provider import Provider
    from app.models.time_slot import TimeSlot

class Product(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    provider_id: UUID = Field(foreign_key="provider.id", nullable=False, ondelete="RESTRICT")
    city_id: UUID | None = Field(default=None, foreign_key="city.id", ondelete="SET NULL")

    type: ProductType = Field(nullable=False)
    title: str = Field(nullable=False)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False
        )

    # Relationships
    provider: "Provider" = Relationship(back_populates="products")
    city: Optional["City"] = Relationship(back_populates="products")
    time_slots: list["TimeSlot"] = Relationship(back_populates="product")

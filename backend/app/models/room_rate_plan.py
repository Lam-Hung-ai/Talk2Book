from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.currency import Currency
    from app.models.hotel import Hotel
    from app.models.room_inventory_daily import RoomInventoryDaily


class RoomRatePlan(SQLModel, table=True):
    __tablename__ = "room_rate_plan"  # type: ignore
    __table_args__ = (UniqueConstraint("hotel_id", "name", name="uq_rrp_hotel_name"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    hotel_id: UUID = Field(foreign_key="hotel.id", nullable=False, ondelete="CASCADE")

    name: str = Field(nullable=False)
    meal_plan: str | None = Field(default=None, max_length=20)

    cancellation_policy: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB)
    )

    currency_code: str = Field(
        foreign_key="currency.code", nullable=False, max_length=3, ondelete="RESTRICT"
    )

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
    hotel: "Hotel" = Relationship(back_populates="room_rate_plans")
    inventory_items: list["RoomInventoryDaily"] = Relationship(
        back_populates="rate_plan"
    )
    currency: "Currency" = Relationship(back_populates="room_rate_plans")

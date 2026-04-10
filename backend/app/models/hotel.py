from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.city import City
    from app.models.hotel_room import HotelRoom
    from app.models.provider import Provider
    from app.models.room_rate_plan import RoomRatePlan


class Hotel(SQLModel, table=True):
    __tablename__ = "hotel"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    provider_id: UUID = Field(
        foreign_key="provider.id", nullable=False, ondelete="RESTRICT"
    )
    city_id: UUID = Field(foreign_key="city.id", nullable=False, ondelete="RESTRICT")

    name: str = Field(nullable=False)
    star_rating: Decimal | None = Field(default=None, max_digits=2, decimal_places=1)
    address: str | None = Field(default=None)

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
    provider: "Provider" = Relationship(back_populates="hotels")
    city: "City" = Relationship(back_populates="hotels")

    rooms: list["HotelRoom"] = Relationship(back_populates="hotel")
    room_rate_plans: list["RoomRatePlan"] = Relationship(back_populates="hotel")

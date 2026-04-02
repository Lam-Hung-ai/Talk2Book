from datetime import UTC, datetime, time
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.city import City
    from app.models.hotel_room import HotelRoom
    from app.models.provider import Provider
    from app.models.room_rate_plan import RoomRatePlan


class Hotel(SQLModel, table=True):
    __tablename__ = "hotel"  # type: ignore

    __table_args__ = (
        CheckConstraint("lat >= -90 AND lat <= 90", name="chk_hotel_lat"),
        CheckConstraint("lng >= -180 AND lng <= 180", name="chk_hotel_lng"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    provider_id: UUID = Field(
        foreign_key="provider.id", nullable=False, ondelete="RESTRICT"
    )
    city_id: UUID = Field(foreign_key="city.id", nullable=False, ondelete="RESTRICT")

    name: str = Field(nullable=False)
    star_rating: Decimal | None = Field(default=None, max_digits=2, decimal_places=1)
    address: str | None = Field(default=None)

    checkin_time: time | None = Field(default=None)
    checkout_time: time | None = Field(default=None)

    lat: Decimal | None = Field(default=None, max_digits=9, decimal_places=6)
    lng: Decimal | None = Field(default=None, max_digits=9, decimal_places=6)

    # Rich fields
    description: str | None = Field(default=None)           # Giới thiệu chung
    images: str | None = Field(default=None)                 # JSON: ["url1","url2",...]
    amenities: str | None = Field(default=None)              # JSON: ["Hồ bơi","Gym",...]
    usp: str | None = Field(default=None)                    # Điểm đặc trưng (gần biển...)
    room_count: int | None = Field(default=None)             # Số lượng phòng
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

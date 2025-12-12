from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.hotel import Hotel
    from app.models.room_inventory_daily import RoomInventoryDaily


class HotelRoom(SQLModel, table=True):
    __tablename__ = "hotel_room"  # type: ignore
    __table_args__ = (
        UniqueConstraint("hotel_id", "code", name="uq_room_hotel_code"),
        CheckConstraint("capacity > 0", name="chk_room_capacity"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    hotel_id: UUID = Field(foreign_key="hotel.id", nullable=False, ondelete="CASCADE")

    code: str | None = Field(default=None)
    capacity: int = Field(nullable=False)
    bed_config: str | None = Field(default=None)

    # Relationships
    hotel: "Hotel" = Relationship(back_populates="rooms")
    inventory_items: list["RoomInventoryDaily"] = Relationship(back_populates="room")

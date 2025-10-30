from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from typing import TYPE_CHECKING, Optional
from uuid import UUID,uuid4

if TYPE_CHECKING:
    from app.models.hotel import Hotel 


class HotelRoom(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("hotel_id", "code", name="uq_hotel_room_code"),
    )

    room_id: UUID = Field(primary_key=True, index=True)
    hotel_id: UUID = Field(foreign_key="hotel.hotel_id", nullable=False)

    code: str = Field(nullable=False)
    capacity: Optional[int] = Field(default=2)
    bed_config: Optional[str] = Field(default=None)


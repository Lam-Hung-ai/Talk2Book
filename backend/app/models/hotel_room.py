from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    pass


class HotelRoom(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("hotel_id", "code", name="uq_hotel_room_code"),)

    room_id: UUID = Field(primary_key=True, index=True)
    hotel_id: UUID = Field(foreign_key="hotel.hotel_id", nullable=False)

    code: str = Field(nullable=False)
    capacity: int | None = Field(default=2)
    bed_config: str | None = Field(default=None)

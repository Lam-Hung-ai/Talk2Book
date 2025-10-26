from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from typing import TYPE_CHECKING, Optional
from uuid import UUID
from datetime import date

if TYPE_CHECKING:
    from .hotel_room import HotelRoom


class RoomInventoryDaily(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("room_id", "rate_plan_id", "stay_date", name="uq_room_rate_date"),
    )

    room_id: UUID = Field(foreign_key="hotelroom.room_id", primary_key=True)
    rate_plan_id: UUID = Field(foreign_key="roomrateplan.rate_plan_id", primary_key=True)

    stay_date: date = Field(primary_key=True)
    allotment: Optional[int] = Field(default=0)
    sold: Optional[int] = Field(default=0)
    stop_sell: Optional[bool] = Field(default=False)

    min_length_of_stay: Optional[int] = Field(default=1)
    max_length_of_stay: Optional[int] = Field(default=None)
    cutoff_hours: Optional[int] = Field(default=None)

    base_price: Optional[float] = Field(default=None)
    tax_inclusive: Optional[bool] = Field(default=True)

  

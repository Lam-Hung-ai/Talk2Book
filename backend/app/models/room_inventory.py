from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    pass


class RoomInventoryDaily(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "room_id", "rate_plan_id", "stay_date", name="uq_room_rate_date"
        ),
    )

    room_id: UUID = Field(foreign_key="hotelroom.room_id", primary_key=True)
    rate_plan_id: UUID = Field(
        foreign_key="roomrateplan.rate_plan_id", primary_key=True
    )

    stay_date: date = Field(primary_key=True)
    allotment: int | None = Field(default=0)
    sold: int | None = Field(default=0)
    stop_sell: bool | None = Field(default=False)

    min_length_of_stay: int | None = Field(default=1)
    max_length_of_stay: int | None = Field(default=None)
    cutoff_hours: int | None = Field(default=None)

    base_price: float | None = Field(default=None)
    tax_inclusive: bool | None = Field(default=True)

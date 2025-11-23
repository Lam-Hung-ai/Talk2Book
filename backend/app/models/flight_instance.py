from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    pass

class FlightInstance(SQLModel, table=True):
    __table_args__ = UniqueConstraint(
        "schedule_id", "flight_date", name="uq_instance_schedule_date"
    )

    instance_id: UUID = Field(primary_key=True, index=True)
    schedule_id: UUID = Field(foreign_key="flightschedule.schedule_id", nullable=False)

    flight_date: date = Field(nullable=False)
    dep_datetime: datetime | None = Field(
        default=None, description="Departure datetime with timezone (timestamptz)"
    )
    arr_datetime: datetime | None = Field(
        default=None, description="Arrival datetime with timezone (timestamptz)"
    )
    status: str | None = Field(
        default="scheduled",
        description="VD: scheduled, departed, arrived, cancelled, delayed...",
    )

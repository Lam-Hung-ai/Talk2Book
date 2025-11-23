from datetime import time
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.flight_instance import FlightInstance
    from app.models.route import Route

class FlightSchedule(SQLModel, table = True):
    _table_args_ = UniqueConstraint ("route_id", "flight_number", name = "uq_schedules_route_flight")

    schedule_id: UUID = Field(primary_key=True, index=True, default_factory=uuid4)
    provider_id: UUID = Field(foreign_key="provider.provider_id", nullable=False)
    route_id: UUID = Field(foreign_key="route.route_id", nullable=False)

    flight_number: str = Field(nullable=False)
    dow: int | None = Field(default=None)
    dep_time: time | None = Field(default=None)
    arr_time: time | None = Field(default=None)
    arrival_day_offset: int | None = Field(default=0)
    aircraft_code: str | None = Field(default=None)

    route: Optional["Route"] = Relationship(back_populates="schedules")
    flight_instances: list["FlightInstance"] = Relationship(back_populates="schedule")

from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from app.models.route import Route
    from app.model.flight_instance from FlightInstance

class FlightSchedule(SQLModel, table = True):
    _table_args_ = UniqueConstraint ("route_id", "flight_number", name = "uq_schedules_route_flight")

    schedule_id: UUID = Field(primary_key=True, index=True, default_factory=uuid4)
    provider_id: UUID = Field(foreign_key="provider.provider_id", nullable=False)
    route_id: UUID = Field(foreign_key="route.route_id", nullable=False)

    flight_number: str = Field(nullable=False)
    dow: Optional[int] = Field(default=None)
    dep_time: Optional[time] = Field(default=None)
    arr_time: Optional[time] = Field(default=None)
    arrival_day_offset: Optional[int] = Field(default=0)
    aircraft_code: Optional[str] = Field(default=None)

    route: Optional["Route"] = Relationship(back_populates="schedules")
    flight_instances: list["FlightInstance"] = Relationship(back_populates="schedule")

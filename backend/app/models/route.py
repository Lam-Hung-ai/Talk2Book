from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, UniqueConstraint
from sqlmodel import CheckConstraint, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.airport import Airport
    from app.models.flight_schedule import FlightSchedule

class Route(SQLModel, table=True):
    __tablename__ = "route"  # type: ignore
    
    __table_args__ = (
        CheckConstraint("origin != destination", name="chk_route_origin_dest"),
        CheckConstraint("distance_km IS NULL OR distance_km > 0", name="chk_route_distance"),
        UniqueConstraint("origin", "destination", name="uq_route_od"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    origin: str = Field(foreign_key="airport.iata", max_length=3, nullable=False)
    destination: str = Field(foreign_key="airport.iata", max_length=3, nullable=False)
    distance_km: int | None = Field(default=None)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), sa_type=DateTime(timezone=True), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), sa_type=DateTime(timezone=True), nullable=False)

    # Relationships
    flight_schedules: list["FlightSchedule"] = Relationship(back_populates="route")
    origin_airport: "Airport" = Relationship(back_populates="depart_routes", sa_relationship_kwargs={"foreign_keys": "[Route.origin]"})
    destination_airport: "Airport" = Relationship(back_populates="arrive_routes", sa_relationship_kwargs={"foreign_keys": "[Route.destination]"})

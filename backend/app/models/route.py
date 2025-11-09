from sqlmodel import Field, SQLModel,Relationship, UniqueConstraint
from uuid import UUID,uuid4
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.flight_schedule import FlightSchedule
    from app.models.airport import Airport

class Route (SQLModel, table=True):
    _table_args_ =  UniqueConstraint ("origin_iata", "destination_iata", name = "uq_routes_od")
    
route_id: UUID = Field (primary_key = True, index = True)
origin: str = Field (foreign_key = "airport.iata", nullable = False, max_length = 3)
destination: str = Field (foreign_key = "airport.iata", nullable = False, max_length = 3)
distance_km: float = Field (nullable = False)

schedules: list["FlightSchedule"] = Relationship(back_populates="route")

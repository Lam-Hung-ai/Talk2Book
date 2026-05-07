from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from app.models.city import City
    from app.models.route import Route


class Airport(SQLModel, table=True):
    __tablename__ = "airport"  # type: ignore

    __table_args__ = (UniqueConstraint("city_id", "name", name="uq_airport_city_name"),)

    iata: str = Field(primary_key=True, max_length=3)
    icao: str | None = Field(max_length=4, unique=True)
    city_id: UUID = Field(nullable=False, foreign_key="city.id", ondelete="RESTRICT")
    name: str = Field(nullable=False)
    timezone: str = Field(nullable=False)

    city: Optional["City"] = Relationship(back_populates="airports")
    depart_routes: list["Route"] = Relationship(
        back_populates="origin_airport",
        sa_relationship_kwargs={"foreign_keys": "[Route.origin]"},
    )
    arrive_routes: list["Route"] = Relationship(
        back_populates="destination_airport",
        sa_relationship_kwargs={"foreign_keys": "[Route.destination]"},
    )

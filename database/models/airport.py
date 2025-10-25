from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship
from uuid import UUID
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from database.models.city import City

class Airport(SQLModel, table=True):
    __tabel_args__ = UniqueConstraint("city", "name", name="uq_airports_city_name")
    
    iata: str | None = Field(primary_key=True, max_length=3)
    itao: str | None = Field(max_length=4, unique=True)
    city_id: UUID = Field(nullable=False, foreign_key="city.id", ondelete="RESTRICT")
    name: str = Field(nullable=False)
    timezone: str = Field(nullable=False)

    city: Optional["City"] = Relationship(back_populates="airports")

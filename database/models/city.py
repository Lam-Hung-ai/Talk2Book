from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship
from uuid import UUID
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from database.models.country import Country
    from database.models.airport import Airport

class City(SQLModel, table = True):
    __table_args__ = (
        UniqueConstraint("country_code", "name", name="uq_cities_country_name")
    )
    id: UUID | None = Field(default=None, primary_key=True)
    country_code: str = Field(max_length=2, foreign_key="country.code", ondelete="RESTRICT")
    name: str = Field(nullable=False)

    country: Optional["Country"] = Relationship(back_populates="cities")
    airports: List["Airport"] = Relationship(back_populates="city")
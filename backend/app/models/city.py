from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from app.models.airport import Airport
    from app.models.country import Country

class City(SQLModel, table = True):
    __table_args__ = (
        UniqueConstraint("country_code", "name", name="uq_cities_country_name"),
    )

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    country_code: str = Field(max_length=2, foreign_key="country.code", ondelete="RESTRICT")
    name: str = Field(nullable=False)

    country: Optional["Country"] = Relationship(back_populates="cities")
    airports: List["Airport"] = Relationship(back_populates="city")
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from app.models.airport import Airport
    from app.models.country import Country
    from app.models.hotel import Hotel
    from app.models.product import Product


class City(SQLModel, table=True):
    __tablename__ = "city"  # type: ignore

    __table_args__ = (
        UniqueConstraint("country_code", "name", name="uq_city_country_name"),
    )

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    country_code: str = Field(
        max_length=2, foreign_key="country.code", ondelete="RESTRICT"
    )
    name: str = Field(nullable=False)

    country: Optional["Country"] = Relationship(back_populates="cities")
    airports: list["Airport"] = Relationship(back_populates="city")
    hotels: list["Hotel"] = Relationship(back_populates="city")
    products: list["Product"] = Relationship(back_populates="city")

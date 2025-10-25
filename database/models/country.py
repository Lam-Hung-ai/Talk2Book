from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from database.models.city import City
    from database.models.currency import Currency

class Country(SQLModel, table = True):
    code: str = Field(primary_key=True, max_length=2)
    name: str = Field(nullable=False)
    currency_code: str = Field(nullable=False, foreign_key="currency.code", ondelete="RESTRICT", max_length=3)

    currency: Optional["City"] = Relationship(back_populates="countries")
    cities: List['Currency'] = Relationship(back_populates="country")
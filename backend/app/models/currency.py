from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .country import Country


class Currency(SQLModel, table=True):
    code: str = Field(nullable=False, max_length=3, primary_key=True)
    name: str = Field(nullable=False)

    countries: list["Country"] = Relationship(back_populates="currency")

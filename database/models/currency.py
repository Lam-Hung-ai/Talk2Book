from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .country import Country

class Currency(SQLModel, table=True):
    code: str = Field(nullable=False, max_length=3, primary_key=True)
    name: str  = Field(nullable=False)

    countries: List["Country"] = Relationship(back_populates="currency")
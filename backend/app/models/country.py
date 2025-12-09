from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.city import City
    from app.models.currency import Currency
    from app.models.provider import Provider


class Country(SQLModel, table=True):
    code: str = Field(primary_key=True, max_length=2)
    name: str = Field(nullable=False)
    currency_code: str = Field(
        nullable=False, foreign_key="currency.code", ondelete="RESTRICT", max_length=3
    )

    currency: Optional["Currency"] = Relationship(back_populates="countries")
    cities: list["City"] = Relationship(back_populates="country")
    providers: list['Provider'] = Relationship(back_populates="country")

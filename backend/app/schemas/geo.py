from uuid import UUID

from pydantic import BaseModel, Field


class CurrencyCreate(BaseModel):
    code: str = Field(min_length=3, max_length=3)
    name: str


class CurrencyRead(CurrencyCreate):
    pass


class CountryCreate(BaseModel):
    code: str = Field(min_length=2, max_length=2)
    name: str
    currency_code: str = Field(min_length=3, max_length=3)


class CountryRead(CountryCreate):
    pass


class CityCreate(BaseModel):
    name: str
    country_code: str = Field(min_length=2, max_length=2)


class CityRead(BaseModel):
    id: UUID
    name: str
    country_code: str = Field(min_length=2, max_length=2)

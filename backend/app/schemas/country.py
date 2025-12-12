# app/schemas/country.py
from pydantic import BaseModel, Field


class CountryRead(BaseModel):
    code: str
    name: str
    currency_code: str

    class Config:
        from_attributes = True


class CountryCreate(BaseModel):
    code: str = Field(max_length=2, min_length=2, description="ISO 3166-1 alpha-2 country code")
    name: str = Field(min_length=1)
    currency_code: str = Field(max_length=3, min_length=3, description="ISO 4217 currency code")


class CountryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    currency_code: str | None = Field(default=None, max_length=3, min_length=3)


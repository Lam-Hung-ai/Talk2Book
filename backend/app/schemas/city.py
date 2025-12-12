# app/schemas/city.py
from uuid import UUID

from pydantic import BaseModel, Field


class CityRead(BaseModel):
    id: UUID
    country_code: str
    name: str

    class Config:
        from_attributes = True


class CityCreate(BaseModel):
    country_code: str = Field(max_length=2, min_length=2, description="ISO 3166-1 alpha-2 country code")
    name: str = Field(min_length=1)


class CityUpdate(BaseModel):
    country_code: str | None = Field(default=None, max_length=2, min_length=2)
    name: str | None = Field(default=None, min_length=1)


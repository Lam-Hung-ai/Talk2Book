# app/schemas/airport.py
from uuid import UUID

from pydantic import BaseModel, Field


class AirportRead(BaseModel):
    iata: str | None
    icao: str | None
    city_id: UUID
    name: str
    timezone: str

    class Config:
        from_attributes = True


class AirportCreate(BaseModel):
    iata: str | None = Field(
        default=None, max_length=3, min_length=3, description="IATA code (3 letters)"
    )
    icao: str | None = Field(
        default=None, max_length=4, min_length=4, description="ICAO code (4 letters)"
    )
    city_id: UUID = Field(description="City ID")
    name: str = Field(min_length=1, description="Airport name")
    timezone: str = Field(
        min_length=1, description="Timezone (e.g., 'Asia/Ho_Chi_Minh')"
    )


class AirportUpdate(BaseModel):
    iata: str | None = Field(default=None, max_length=3, min_length=3)
    icao: str | None = Field(default=None, max_length=4, min_length=4)
    city_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1)
    timezone: str | None = Field(default=None, min_length=1)

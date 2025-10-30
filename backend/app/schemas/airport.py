from pydantic import BaseModel, Field
from uuid import UUID

class AirportCreate(BaseModel):
    iata: str = Field(min_length=3, max_length=3)
    icao: str | None = Field(default=None, min_length=4, max_length=4)
    city_id: UUID
    name: str
    timezone: str

class AirportUpdate(BaseModel):
    icao: str | None = Field(default=None, min_length=4, max_length=4)
    name: str | None = None
    timezone: str | None = None

class AirportRead(AirportCreate):
    pass
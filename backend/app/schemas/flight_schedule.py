from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, Field


class AmenitiesInfo(BaseModel):
    items: list[str] = Field(default_factory=list)
    carry_on_kg: float | None = None
    checked_baggage_kg: float | None = None
    has_meal: bool = False
    has_lounge: bool = False


class FlightScheduleBase(BaseModel):
    provider_id: UUID
    route_id: UUID
    flight_number: str = Field(min_length=1)
    dow: str = Field(
        min_length=7,
        max_length=7,
        description="Bitstring for days of week, e.g. 1000000 for Monday",
    )
    dep_time: time
    arr_time: time
    arrival_day_offset: int = Field(default=0)
    amenities: AmenitiesInfo | None = None


class FlightScheduleCreate(FlightScheduleBase):
    pass


class FlightScheduleUpdate(BaseModel):
    provider_id: UUID | None = None
    route_id: UUID | None = None
    flight_number: str | None = Field(default=None, min_length=1)
    dow: str | None = Field(default=None, min_length=7, max_length=7)
    dep_time: time | None = None
    arr_time: time | None = None
    arrival_day_offset: int | None = None
    amenities: AmenitiesInfo | None = None


class FlightScheduleRead(FlightScheduleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

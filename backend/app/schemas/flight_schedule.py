from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, Field


class FlightScheduleBase(BaseModel):
    provider_id: UUID
    route_id: UUID
    flight_number: str = Field(min_length=1, max_length=50)
    dow: str = Field(description="Bitstring representing Days of Week (e.g., 1000000)")
    dep_time: time
    arr_time: time
    arrival_day_offset: int = Field(default=0)
    aircraft_code: str | None = None


class FlightScheduleCreate(FlightScheduleBase):
    pass


class FlightScheduleUpdate(BaseModel):
    provider_id: UUID | None = None
    route_id: UUID | None = None
    flight_number: str | None = Field(default=None, min_length=1, max_length=50)
    dow: str | None = None
    dep_time: time | None = None
    arr_time: time | None = None
    arrival_day_offset: int | None = None
    aircraft_code: str | None = None


class FlightScheduleRead(FlightScheduleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


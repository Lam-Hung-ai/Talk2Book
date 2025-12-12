from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, Field


class FlightInstanceBase(BaseModel):
    schedule_id: UUID
    flight_date: date
    dep_datetime: datetime
    arr_datetime: datetime
    status: str = Field(default="scheduled", max_length=20)


class FlightInstanceCreate(FlightInstanceBase):
    pass


class FlightInstanceUpdate(BaseModel):
    schedule_id: UUID | None = None
    flight_date: date | None = None
    dep_datetime: datetime | None = None
    arr_datetime: datetime | None = None
    status: str | None = Field(default=None, max_length=20)


class FlightInstanceRead(FlightInstanceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


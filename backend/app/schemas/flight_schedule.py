from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, Field


class FlightScheduleBase(BaseModel):
    provider_id: UUID
    route_id: UUID
    flight_number: str = Field(min_length=1)
    dow: str = Field(min_length=7, max_length=7, description="Bitstring for days of week, e.g. 1000000 for Monday")
    dep_time: time
    arr_time: time
    arrival_day_offset: int = Field(default=0)
    aircraft_code: str | None = None
    # Rich fields
    cabin_class: str | None = None      # Economy, Business, First (từ danh mục)
    ticket_type: str | None = None      # Loại vé (từ danh mục)
    amenities: list[str] | None = None
    price_from: float | None = None     # Giá tham khảo chưa VAT


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
    aircraft_code: str | None = None
    cabin_class: str | None = None
    ticket_type: str | None = None
    amenities: list[str] | None = None
    price_from: float | None = None


class FlightScheduleRead(FlightScheduleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

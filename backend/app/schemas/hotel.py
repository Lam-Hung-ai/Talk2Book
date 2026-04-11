# app/schemas/hotel.py
from datetime import datetime, time
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class HotelBase(BaseModel):
    provider_id: UUID
    city_id: UUID
    name: str = Field(min_length=1)
    star_rating: Decimal | None = Field(default=None, max_digits=2, decimal_places=1, ge=0, le=5)
    address: str | None = None
    checkin_time: time | None = None
    checkout_time: time | None = None
    lat: Decimal | None = Field(default=None, max_digits=9, decimal_places=6, ge=-90, le=90)
    lng: Decimal | None = Field(default=None, max_digits=9, decimal_places=6, ge=-180, le=180)
    # Rich fields
    description: str | None = None
    images: list[str] | None = None
    amenities: list[str] | None = None
    usp: str | None = None
    room_count: int | None = None


class HotelCreate(HotelBase):
    pass


class HotelUpdate(BaseModel):
    provider_id: UUID | None = None
    city_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1)
    star_rating: Decimal | None = Field(default=None, max_digits=2, decimal_places=1, ge=0, le=5)
    address: str | None = None
    checkin_time: time | None = None
    checkout_time: time | None = None
    lat: Decimal | None = Field(default=None, max_digits=9, decimal_places=6, ge=-90, le=90)
    lng: Decimal | None = Field(default=None, max_digits=9, decimal_places=6, ge=-180, le=180)
    description: str | None = None
    images: list[str] | None = None
    amenities: list[str] | None = None
    usp: str | None = None
    room_count: int | None = None


class HotelRead(HotelBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# app/schemas/hotel.py
from datetime import datetime, time
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import UserStatus


class HotelBase(BaseModel):
    provider_id: UUID
    city_id: UUID
    name: str = Field(min_length=1, max_length=255)
    star_rating: Decimal | None = Field(default=None, ge=0, le=5, decimal_places=1)
    address: str | None = None
    checkin_time: time | None = None
    checkout_time: time | None = None
    lat: Decimal | None = Field(default=None, ge=-90, le=90, decimal_places=6)
    lng: Decimal | None = Field(default=None, ge=-180, le=180, decimal_places=6)


class HotelCreate(HotelBase):
    pass


class HotelUpdate(BaseModel):
    provider_id: UUID | None = None
    city_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    star_rating: Decimal | None = Field(default=None, ge=0, le=5, decimal_places=1)
    address: str | None = None
    checkin_time: time | None = None
    checkout_time: time | None = None
    lat: Decimal | None = Field(default=None, ge=-90, le=90, decimal_places=6)
    lng: Decimal | None = Field(default=None, ge=-180, le=180, decimal_places=6)


class HotelRead(HotelBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# app/schemas/hotel_room.py
from uuid import UUID

from pydantic import BaseModel, Field


class HotelRoomBase(BaseModel):
    hotel_id: UUID
    code: str | None = None
    capacity: int = Field(gt=0)
    bed_config: str | None = None
    # Rich fields
    room_type: str | None = None  # Loại phòng (từ danh mục)
    area_sqm: float | None = None  # Diện tích m²
    view_type: str | None = None  # Tầm nhìn (từ danh mục)
    amenities: list[str] | None = None
    service_package: str | None = None
    cancellation_policy: str | None = None
    description: str | None = None
    images: list[str] | None = None


class HotelRoomCreate(HotelRoomBase):
    pass


class HotelRoomUpdate(BaseModel):
    hotel_id: UUID | None = None
    code: str | None = None
    capacity: int | None = Field(default=None, gt=0)
    bed_config: str | None = None
    room_type: str | None = None
    area_sqm: float | None = None
    view_type: str | None = None
    amenities: list[str] | None = None
    service_package: str | None = None
    cancellation_policy: str | None = None
    description: str | None = None
    images: list[str] | None = None


class HotelRoomRead(HotelRoomBase):
    id: UUID

    class Config:
        from_attributes = True

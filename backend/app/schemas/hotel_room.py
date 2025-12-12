# app/schemas/hotel_room.py
from uuid import UUID

from pydantic import BaseModel, Field


class HotelRoomBase(BaseModel):
    hotel_id: UUID
    code: str | None = None
    capacity: int = Field(gt=0, description="Số người tối đa")
    bed_config: str | None = None


class HotelRoomCreate(HotelRoomBase):
    pass


class HotelRoomUpdate(BaseModel):
    hotel_id: UUID | None = None
    code: str | None = None
    capacity: int | None = Field(default=None, gt=0)
    bed_config: str | None = None


class HotelRoomRead(HotelRoomBase):
    id: UUID

    class Config:
        from_attributes = True


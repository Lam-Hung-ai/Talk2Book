# app/schemas/room_inventory_daily.py
from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class RoomInventoryDailyBase(BaseModel):
    room_id: UUID
    rate_plan_id: UUID
    stay_date: date
    allotment: int = Field(ge=0, description="Tổng số phòng có sẵn")
    sold: int = Field(default=0, ge=0, description="Số phòng đã bán")
    stop_sell: bool = Field(default=False, description="Có dừng bán không")
    base_price: Decimal = Field(ge=0, decimal_places=2, description="Giá cơ bản")


class RoomInventoryDailyCreate(RoomInventoryDailyBase):
    pass


class RoomInventoryDailyUpdate(BaseModel):
    room_id: UUID | None = None
    rate_plan_id: UUID | None = None
    stay_date: date | None = None
    allotment: int | None = Field(default=None, ge=0)
    sold: int | None = Field(default=None, ge=0)
    stop_sell: bool | None = None
    base_price: Decimal | None = Field(default=None, ge=0, decimal_places=2)


class RoomInventoryDailyRead(RoomInventoryDailyBase):
    class Config:
        from_attributes = True


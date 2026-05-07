# app/schemas/room_rate_plan.py
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class RoomRatePlanBase(BaseModel):
    hotel_id: UUID
    name: str = Field(min_length=1)
    meal_plan: str | None = Field(default=None, max_length=20)
    cancellation_policy: dict[str, Any] | None = None
    currency_code: str = Field(max_length=3, min_length=3)


class RoomRatePlanCreate(RoomRatePlanBase):
    pass


class RoomRatePlanUpdate(BaseModel):
    hotel_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1)
    meal_plan: str | None = Field(default=None, max_length=20)
    cancellation_policy: dict[str, Any] | None = None
    currency_code: str | None = Field(default=None, max_length=3, min_length=3)


class RoomRatePlanRead(RoomRatePlanBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# app/schemas/time_slot.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TimeSlotBase(BaseModel):
    product_id: UUID
    start_datetime: datetime
    end_datetime: datetime


class TimeSlotCreate(TimeSlotBase):
    pass


class TimeSlotUpdate(BaseModel):
    product_id: UUID | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None


class TimeSlotRead(TimeSlotBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


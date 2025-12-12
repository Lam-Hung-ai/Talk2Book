from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class BookingAuditLogBase(BaseModel):
    booking_id: UUID
    actor_type: str | None = None
    actor_id: UUID | None = None
    action: str = Field(min_length=1)
    from_state: str | None = None
    to_state: str | None = None
    meta: dict[str, Any] | None = None


class BookingAuditLogCreate(BookingAuditLogBase):
    pass


class BookingAuditLogUpdate(BaseModel):
    actor_type: str | None = None
    actor_id: UUID | None = None
    action: str | None = Field(default=None, min_length=1)
    from_state: str | None = None
    to_state: str | None = None
    meta: dict[str, Any] | None = None


class BookingAuditLogRead(BookingAuditLogBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


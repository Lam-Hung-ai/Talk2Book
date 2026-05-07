from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import TicketType


class TicketBase(BaseModel):
    item_id: UUID
    type: TicketType
    code: str = Field(min_length=1)


class TicketCreate(TicketBase):
    issued_at: datetime | None = None


class TicketUpdate(BaseModel):
    type: TicketType | None = None
    code: str | None = Field(default=None, min_length=1)
    issued_at: datetime | None = None


class TicketRead(TicketBase):
    id: UUID
    issued_at: datetime

    class Config:
        from_attributes = True

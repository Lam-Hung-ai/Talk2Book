# app/schemas/slot_inventory.py
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class SlotInventoryBase(BaseModel):
    slot_id: UUID
    capacity: int = Field(gt=0)
    sold: int = Field(default=0, ge=0)
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    currency_code: str = Field(min_length=3, max_length=3)


class SlotInventoryCreate(SlotInventoryBase):
    pass


class SlotInventoryUpdate(BaseModel):
    capacity: int | None = Field(default=None, gt=0)
    sold: int | None = Field(default=None, ge=0)
    price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    currency_code: str | None = Field(default=None, min_length=3, max_length=3)


class SlotInventoryRead(SlotInventoryBase):
    class Config:
        from_attributes = True


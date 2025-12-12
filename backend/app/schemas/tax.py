# app/schemas/tax.py
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class TaxBase(BaseModel):
    scope: str = Field(max_length=20)
    name: str
    rate: Decimal | None = Field(default=None, ge=0, le=1)
    amount: Decimal | None = Field(default=None, ge=0)
    currency_code: str | None = Field(default=None, max_length=3)


class TaxCreate(TaxBase):
    pass


class TaxUpdate(BaseModel):
    scope: str | None = Field(default=None, max_length=20)
    name: str | None = None
    rate: Decimal | None = Field(default=None, ge=0, le=1)
    amount: Decimal | None = Field(default=None, ge=0)
    currency_code: str | None = Field(default=None, max_length=3)


class TaxRead(TaxBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


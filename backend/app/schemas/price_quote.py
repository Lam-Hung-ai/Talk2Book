# app/schemas/price_quote.py
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class PriceQuoteBase(BaseModel):
    user_id: str | None = None
    vertical: str = Field(max_length=20)
    payload: dict[str, Any]
    currency_code: str = Field(max_length=3)
    total_amount: Decimal = Field(ge=0)
    expires_at: datetime


class PriceQuoteCreate(PriceQuoteBase):
    pass


class PriceQuoteUpdate(BaseModel):
    user_id: str | None = None
    vertical: str | None = Field(default=None, max_length=20)
    payload: dict[str, Any] | None = None
    currency_code: str | None = Field(default=None, max_length=3)
    total_amount: Decimal | None = Field(default=None, ge=0)
    expires_at: datetime | None = None


class PriceQuoteRead(PriceQuoteBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

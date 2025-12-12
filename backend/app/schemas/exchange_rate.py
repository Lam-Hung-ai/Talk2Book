# app/schemas/exchange_rate.py
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class ExchangeRateBase(BaseModel):
    rate_date: date
    base: str = Field(max_length=3)
    quote: str = Field(max_length=3)
    rate: Decimal = Field(gt=0)


class ExchangeRateCreate(ExchangeRateBase):
    pass


class ExchangeRateUpdate(BaseModel):
    rate_date: date | None = None
    base: str | None = Field(default=None, max_length=3)
    quote: str | None = Field(default=None, max_length=3)
    rate: Decimal | None = Field(default=None, gt=0)


class ExchangeRateRead(ExchangeRateBase):
    class Config:
        from_attributes = True


# app/schemas/contract.py
from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ContractBase(BaseModel):
    provider_id: UUID
    effective_from: date
    effective_to: date | None = None
    commission_pct: Decimal | None = Field(default=None, ge=0, le=100)
    currency_code: str = Field(max_length=3)


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    provider_id: UUID | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    commission_pct: Decimal | None = Field(default=None, ge=0, le=100)
    currency_code: str | None = Field(default=None, max_length=3)


class ContractRead(ContractBase):
    id: UUID

    class Config:
        from_attributes = True


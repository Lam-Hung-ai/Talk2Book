from typing import Optional, Any
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON


class PriceQuote(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    created_at: Optional[datetime] = Field(default=datetime.now())
    expires_at: Optional[datetime] = Field(default=None)
    currency_code: str = Field(nullable=False, foreign_key="currency.code", max_length=3)
    total_amount: float = Field(nullable=False)
    # Arbitrary JSON detail about the quote (line items, taxes applied, rate snapshot)
    quote_data: Optional[Any] = Field(default=None, sa_column=Column(JSON))
    integrity_token: Optional[str] = Field(default=None, max_length=128, description="Token to validate quote integrity at booking time")

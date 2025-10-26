from typing import TYPE_CHECKING, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON

if TYPE_CHECKING:
    from .user import User

class PriceQuote(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID | None = Field(default=None, foreign_key="user.id")
    created_at: datetime | None = Field(default=datetime.now())
    expires_at: datetime | None = Field(default=None)
    currency_code: str = Field(nullable=False, foreign_key="currency.code", max_length=3)
    total_amount: float = Field(nullable=False)
    # Arbitrary JSON detail about the quote (line items, taxes applied, rate snapshot)
    quote_data: Any | None = Field(default=None, sa_column=Column(JSON))
    integrity_token: str | None = Field(default=None, max_length=128, description="Token to validate quote integrity at booking time")

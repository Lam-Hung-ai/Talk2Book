from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    from .currency import Currency

class Tax(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    code: str = Field(nullable=False, unique=True, max_length=64)
    name: str = Field(nullable=False)
    percent: float | None = Field(default=None, description="Percent rate (0-100)")
    amount: float | None = Field(default=None, description="Fixed amount in `currency_code`")
    currency_code: str | None = Field(default=None, foreign_key="currency.code", max_length=3)
    description: str | None = Field(default=None)
    created_at: datetime | None = Field(default=datetime.now())

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, SQLModel

class Tax(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    code: str = Field(nullable=False, unique=True, max_length=64)
    name: str = Field(nullable=False)
    percent: Optional[float] = Field(default=None, description="Percent rate (0-100)")
    amount: Optional[float] = Field(default=None, description="Fixed amount in `currency_code`")
    currency_code: Optional[str] = Field(default=None, foreign_key="currency.code", max_length=3)
    description: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default=datetime.now())

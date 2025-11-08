from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, SQLModel

class Coupon(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    code: str = Field(nullable=False, unique=True, max_length=64)
    description: Optional[str] = Field(default=None)
    percent: Optional[float] = Field(default=None, description="Percent discount 0-100")
    amount: Optional[float] = Field(default=None, description="Fixed amount discount in `currency_code`")
    currency_code: Optional[str] = Field(default=None, foreign_key="currency.code", max_length=3)
    start_at: Optional[datetime] = Field(default=None)
    end_at: Optional[datetime] = Field(default=None)
    usage_limit: Optional[int] = Field(default=None, description="Total times coupon can be used across all users")
    per_user_limit: Optional[int] = Field(default=None, description="Max uses per user")
    active: bool = Field(default=True)
    created_at: Optional[datetime] = Field(default=datetime.now())

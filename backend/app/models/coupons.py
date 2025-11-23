from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    pass


class Coupon(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    code: str = Field(nullable=False, unique=True, max_length=64)
    description: str | None = Field(default=None)
    percent: float | None = Field(default=None, description="Percent discount 0-100")
    amount: float | None = Field(
        default=None, description="Fixed amount discount in `currency_code`"
    )
    currency_code: str | None = Field(
        default=None, foreign_key="currency.code", max_length=3
    )
    start_at: datetime | None = Field(default=None)
    end_at: datetime | None = Field(default=None)
    usage_limit: int | None = Field(
        default=None, description="Total times coupon can be used across all users"
    )
    per_user_limit: int | None = Field(default=None, description="Max uses per user")
    active: bool = Field(default=True)
    created_at: datetime | None = Field(default=datetime.now())

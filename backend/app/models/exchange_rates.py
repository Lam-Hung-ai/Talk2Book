from typing import TYPE_CHECKING
from datetime import date, datetime
from sqlmodel import Field, SQLModel, UniqueConstraint
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .currency import Currency


class ExchangeRate(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "rate_date", "base_currency", "target_currency", name="uq_exrates_date_pair"
        ),
    )

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    rate_date: date = Field(nullable=False)
    base_currency: str = Field(
        nullable=False, foreign_key="currency.code", max_length=3
    )
    target_currency: str = Field(
        nullable=False, foreign_key="currency.code", max_length=3
    )
    rate: float = Field(
        nullable=False,
        description="Units of target currency per one unit of base currency",
    )
    created_at: datetime | None = Field(default=datetime.now())

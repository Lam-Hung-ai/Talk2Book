from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Column, Numeric
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.currency import Currency
    from app.models.provider import Provider


class Contract(SQLModel, table=True):
    __tablename__ = "contract"  # type: ignore

    __table_args__ = (
        CheckConstraint(
            "(commission_pct IS NULL) OR (commission_pct >= 0 AND commission_pct <= 100)",
            name="check_commission_pct",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    provider_id: UUID = Field(
        foreign_key="provider.id", nullable=False, ondelete="CASCADE"
    )

    effective_from: date = Field(nullable=False)
    effective_to: date | None = Field(default=None)

    commission_pct: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(5, 2))
    )

    currency_code: str = Field(
        foreign_key="currency.code", nullable=False, max_length=3, ondelete="RESTRICT"
    )

    provider: "Provider" = Relationship(back_populates="contracts")
    currency: "Currency" = Relationship(back_populates="contracts")

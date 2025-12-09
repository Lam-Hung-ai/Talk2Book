from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    pass



class RoomRatePlan(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("hotel_id", "name", name="uq_rateplans_hotel_name"),
    )

    rate_plan_id: UUID = Field(primary_key=True, index=True)
    hotel_id: UUID = Field(foreign_key="hotel.hotel_id", nullable=False)

    name: str = Field(nullable=False)
    meal_plan: str | None = Field(
        default=None,
        max_length=50,
    )

    cancellation_policy: dict | None = Field(
        default=None,
        sa_column=Column(JSONB),
    )

    currency_code: str = Field(
        foreign_key="currency.code", nullable=False, max_length=3
    )

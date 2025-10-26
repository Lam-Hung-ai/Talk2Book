from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from typing import TYPE_CHECKING, Optional, List
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column

if TYPE_CHECKING:
    from .hotel import Hotel
     


class RoomRatePlan(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("hotel_id", "name", name="uq_rateplans_hotel_name"),
    )

    rate_plan_id: UUID = Field(primary_key=True, index=True)
    hotel_id: UUID = Field(foreign_key="hotel.hotel_id", nullable=False)

    name: str = Field(nullable=False)
    meal_plan: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    cancellation_policy: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSONB),
    )

    currency_code: str = Field(
        foreign_key="currency.code",  
        nullable=False,
        max_length=3
    )

   

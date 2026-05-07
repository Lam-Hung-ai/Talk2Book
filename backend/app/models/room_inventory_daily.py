from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import CheckConstraint, Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from app.models.hotel_room import HotelRoom
    from app.models.room_rate_plan import RoomRatePlan


class RoomInventoryDaily(SQLModel, table=True):
    __tablename__ = "room_inventory_daily"  # type: ignore
    __table_args__ = (
        UniqueConstraint(
            "room_id", "rate_plan_id", "stay_date", name="uq_room_rate_date"
        ),
        CheckConstraint("sold <= allotment", name="chk_rid_sold_allotment"),
        CheckConstraint("allotment > 0", name="chk_rid_allotment_positive"),
        CheckConstraint("base_price >= 0", name="chk_rid_price_positive"),
    )

    room_id: UUID = Field(
        foreign_key="hotel_room.id",
        primary_key=True,
        nullable=False,
        ondelete="CASCADE",
    )
    rate_plan_id: UUID = Field(
        foreign_key="room_rate_plan.id",
        primary_key=True,
        nullable=False,
        ondelete="CASCADE",
    )
    stay_date: date = Field(primary_key=True, nullable=False)

    allotment: int = Field(nullable=False)
    sold: int = Field(default=0, nullable=False)
    stop_sell: bool = Field(default=False, nullable=False)
    base_price: Decimal = Field(nullable=False, max_digits=12, decimal_places=2)

    # Relationships
    room: "HotelRoom" = Relationship(back_populates="inventory_items")
    rate_plan: "RoomRatePlan" = Relationship(back_populates="inventory_items")

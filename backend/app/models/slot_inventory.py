from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.currency import Currency
    from app.models.time_slot import TimeSlot

class SlotInventory(SQLModel, table=True):
    __tablename__ = "slot_inventory"  # type: ignore
    __table_args__ = (
        CheckConstraint("sold <= capacity", name="chk_inventory_sold_capacity"),
        CheckConstraint("capacity > 0", name="chk_inventory_capacity_positive"),
        CheckConstraint("price >= 0", name="chk_inventory_price_positive"),
    )

    slot_id: UUID = Field(
        primary_key=True,
        foreign_key="time_slot.id",
        ondelete="CASCADE"
    )
    capacity: int = Field(nullable=False)
    sold: int = Field(default=0, nullable=False)

    price: Decimal = Field(default=0, max_digits=12, decimal_places=2, nullable=False)
    currency_code: str = Field(
        max_length=3,
        foreign_key="currency.code",
        nullable=False,
        ondelete="RESTRICT"
    )

    # Relationships
    time_slot: "TimeSlot" = Relationship(back_populates="inventory")
    currency: "Currency" = Relationship(back_populates="inventories")

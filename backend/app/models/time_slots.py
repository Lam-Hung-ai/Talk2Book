from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from .products import Product
    from .slot_inventory import SlotInventory

class TimeSlot(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("product_id", "start_at", name="uq_timeslots_product_start"),)

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    product_id: UUID = Field(nullable=False, foreign_key="product.id", ondelete="RESTRICT")
    start_at: datetime = Field(nullable=False)
    end_at: datetime | None = Field(default=None)
    notes: str | None = Field(default=None)

    product: Optional["Product"] = Relationship(back_populates="time_slots")
    inventory: Optional["SlotInventory"] = Relationship(back_populates="time_slot")

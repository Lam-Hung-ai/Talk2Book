from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import DateTime, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.slot_inventory import SlotInventory

class TimeSlot(SQLModel, table=True):

    __tablename__ = "time_slot"  # type: ignore
    __table_args__ = (
        CheckConstraint("start_datetime < end_datetime", name="chk_slot_dates"),
        UniqueConstraint("product_id", "start_datetime", "end_datetime", name="uq_slot_unique"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    product_id: UUID = Field(foreign_key="product.id", nullable=False, ondelete="CASCADE")
    start_datetime: datetime = Field(sa_type=DateTime(timezone=True), nullable=False)
    end_datetime: datetime = Field(sa_type=DateTime(timezone=True), nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),
        nullable=False
    )

    # Relationships
    product: "Product" = Relationship(back_populates="time_slots")
    inventory: Optional["SlotInventory"] = Relationship(back_populates="time_slot")

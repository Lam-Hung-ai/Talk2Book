from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

class SlotInventory(SQLModel, table=True):
    time_slot_id: UUID = Field(nullable=False, primary_key=True, foreign_key="time_slot.id", ondelete="CASCADE")
    total: int = Field(default=0, nullable=False)
    sold: int = Field(default=0, nullable=False)
    price: float = Field(nullable=False)
    currency_code: str = Field(nullable=False, foreign_key="currency.code", max_length=3)
    updated_at: Optional[datetime] = Field(default=datetime.now())

    time_slot: Optional["TimeSlot"] = Relationship(back_populates="inventory")

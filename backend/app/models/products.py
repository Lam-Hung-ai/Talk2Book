from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from .time_slots import TimeSlot

class Product(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("code", name="uq_products_code"),)

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    code: str = Field(nullable=False, unique=True, max_length=64)
    name: str = Field(nullable=False)
    description: str | None = Field(default=None)
    service_type: str | None = Field(default=None, max_length=32)  # e.g. 'tour', 'transfer'
    duration_minutes: int | None = Field(default=None)
    active: bool = Field(default=True)
    created_at: datetime | None = Field(default=datetime.now())

    time_slots: List["TimeSlot"] = Relationship(back_populates="product")

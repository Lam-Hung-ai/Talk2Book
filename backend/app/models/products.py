from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

class Product(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("code", name="uq_products_code"),)

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    code: str = Field(nullable=False, unique=True, max_length=64)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    service_type: Optional[str] = Field(default=None, max_length=32)  # e.g. 'tour', 'transfer'
    duration_minutes: Optional[int] = Field(default=None)
    active: bool = Field(default=True)
    created_at: Optional[datetime] = Field(default=datetime.now())

    time_slots: List["TimeSlot"] = Relationship(back_populates="product")

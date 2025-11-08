from typing import List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, JSON

class BookingStatus(str):
    created = "created"
    paid = "paid"
    canceled = "canceled"
    failed = "failed"
    refunded = "refunded"

class Booking(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    status: Optional[str] = Field(default=BookingStatus.created)
    created_at: Optional[datetime] = Field(default=datetime.now())
    updated_at: Optional[datetime] = Field(default=datetime.now())
    total_amount: Optional[float] = Field(default=0.0)
    currency_code: Optional[str] = Field(default=None, foreign_key="currency.code", max_length=3)
    quote_id: Optional[UUID] = Field(default=None, foreign_key="pricequote.id")
    payment_method: Optional[str] = Field(default=None)
    paid_at: Optional[datetime] = Field(default=None)
    meta: Optional[Any] = Field(default=None, sa_column=Column(JSON))

    items: List["BookingItem"] = Relationship(back_populates="booking")

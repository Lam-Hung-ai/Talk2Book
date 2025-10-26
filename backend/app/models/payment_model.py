from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    booking_id: Optional[int] = Field(default=None)
    gateway: str
    amount: float
    currency: str = "VND"
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    transactions: List["PaymentTransaction"] = Relationship(back_populates="payment")
    refunds: List["Refund"] = Relationship(back_populates="payment")
    user: Optional["User"] = Relationship(back_populates="payments")

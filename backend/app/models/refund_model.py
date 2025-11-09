from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional


class Refund(SQLModel, table=True):
    __tablename__ = "refunds"

    id: Optional[int] = Field(default=None, primary_key=True)
    payment_id: int = Field(foreign_key="payments.id")
    amount: float
    reason: str
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    payment: Optional["Payment"] = Relationship(back_populates="refunds")

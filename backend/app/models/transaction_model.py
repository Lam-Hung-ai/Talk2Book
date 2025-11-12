from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

from app.models.payment_model import Payment


class PaymentTransaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    payment_id: int = Field(foreign_key="payment.id")
    step: str
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    payment: Optional["Payment"] = Relationship(back_populates="transactions")

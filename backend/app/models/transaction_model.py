from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.payment_model import Payment


class PaymentTransaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    payment_id: int = Field(foreign_key="payment.id")
    step: str
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    payment: Optional["Payment"] = Relationship(back_populates="transactions")

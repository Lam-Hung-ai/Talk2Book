from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.refund_model import Refund
    from app.models.transaction_model import PaymentTransaction
    from app.models.user_model import User


class Payment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    booking_id: int | None = Field(default=None)
    gateway: str
    amount: float
    currency: str = "VND"
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    transactions: list["PaymentTransaction"] = Relationship(back_populates="payment")
    refunds: list["Refund"] = Relationship(back_populates="payment")
    user: Optional["User"] = Relationship(back_populates="payment")

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from app.models.transaction_model import PaymentTransaction
    from app.models.refund_model import Refund
    from app.models.user_model import User


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    booking_id: Optional[int] = Field(default=None)
    gateway: str
    amount: float
    currency: str = "VND"
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    transactions: List["PaymentTransaction"] = Relationship(back_populates="payment")
    refunds: List["Refund"] = Relationship(back_populates="payment")
    user: Optional["User"] = Relationship(back_populates="payment")

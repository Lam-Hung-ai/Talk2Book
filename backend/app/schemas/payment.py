# app/schemas/payment.py
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import PaymentStatus


class PaymentRead(BaseModel):
    """Schema để đọc thông tin Payment"""

    id: UUID
    booking_id: UUID
    provider: str
    amount: Decimal
    currency_code: str
    status: PaymentStatus
    idempotency_key: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    """Schema để tạo Payment mới"""

    booking_id: UUID = Field(..., description="ID của booking")
    provider: str = Field(
        ..., description="Payment gateway (VNPay, Momo, ZaloPay, etc.)"
    )
    amount: Decimal = Field(..., gt=0, description="Số tiền thanh toán")
    currency_code: str = Field(
        ..., max_length=3, description="Mã tiền tệ (VND, USD, etc.)"
    )
    status: PaymentStatus = Field(
        default=PaymentStatus.pending, description="Trạng thái payment"
    )
    idempotency_key: str | None = Field(
        default=None, description="Key để tránh duplicate payment"
    )


class PaymentUpdate(BaseModel):
    """Schema để cập nhật Payment"""

    provider: str | None = Field(default=None, description="Payment gateway")
    amount: Decimal | None = Field(default=None, gt=0, description="Số tiền thanh toán")
    currency_code: str | None = Field(
        default=None, max_length=3, description="Mã tiền tệ"
    )
    status: PaymentStatus | None = Field(default=None, description="Trạng thái payment")
    idempotency_key: str | None = Field(
        default=None, description="Key để tránh duplicate payment"
    )

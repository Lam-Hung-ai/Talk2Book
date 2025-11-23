from collections.abc import Sequence
from datetime import datetime

from pydantic import BaseModel, Field


class PaymentTransactionBase(BaseModel):
    """Base schema cho PaymentTransaction"""
    payment_id: int = Field(..., description="ID của payment")
    step: str = Field(..., description="Bước trong quy trình thanh toán")
    status: str = Field(..., description="Trạng thái: pending, processing, success, failed")


class PaymentTransactionCreate(PaymentTransactionBase):
    """Schema để tạo PaymentTransaction mới"""
    pass


class PaymentTransactionUpdate(BaseModel):
    """Schema để cập nhật PaymentTransaction"""
    step: str | None = None
    status: str | None = None


class PaymentTransactionResponse(PaymentTransactionBase):
    """Schema response cho PaymentTransaction"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentTransactionListResponse(BaseModel):
    """Schema cho danh sách PaymentTransaction với pagination"""
    total: int
    items: Sequence[PaymentTransactionResponse]
    skip: int
    limit: int

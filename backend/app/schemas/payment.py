from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PaymentBase(BaseModel):
    """Base schema cho Payment"""
    user_id: UUID
    booking_id: int | None = None
    gateway: str = Field(..., description="Payment gateway (VNPay, Momo, ZaloPay, etc.)")
    amount: float = Field(..., gt=0, description="Số tiền thanh toán")
    currency: str = Field(default="VND", description="Loại tiền tệ")
    status: str = Field(..., description="Trạng thái: pending, completed, failed, refunded")


class PaymentCreate(PaymentBase):
    """Schema để tạo Payment mới"""
    pass


class PaymentUpdate(BaseModel):
    """Schema để cập nhật Payment"""
    booking_id: int | None = None
    gateway: str | None = None
    amount: float | None = Field(None, gt=0)
    currency: str | None = None
    status: str | None = None


class PaymentResponse(PaymentBase):
    """Schema response cho Payment"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentListResponse(BaseModel):
    """Schema cho danh sách Payment với pagination"""
    total: int
    items: Sequence[PaymentResponse]
    skip: int
    limit: int

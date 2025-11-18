from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID


class PaymentBase(BaseModel):
    """Base schema cho Payment"""
    user_id: UUID
    booking_id: Optional[int] = None
    gateway: str = Field(..., description="Payment gateway (VNPay, Momo, ZaloPay, etc.)")
    amount: float = Field(..., gt=0, description="Số tiền thanh toán")
    currency: str = Field(default="VND", description="Loại tiền tệ")
    status: str = Field(..., description="Trạng thái: pending, completed, failed, refunded")


class PaymentCreate(PaymentBase):
    """Schema để tạo Payment mới"""
    pass


class PaymentUpdate(BaseModel):
    """Schema để cập nhật Payment"""
    booking_id: Optional[int] = None
    gateway: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = None
    status: Optional[str] = None


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

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Sequence


class RefundBase(BaseModel):
    """Base schema cho Refund"""
    payment_id: int = Field(..., description="ID của payment cần hoàn tiền")
    amount: float = Field(..., gt=0, description="Số tiền hoàn lại")
    reason: str = Field(..., min_length=1, description="Lý do hoàn tiền")
    status: str = Field(..., description="Trạng thái: pending, approved, rejected, completed")


class RefundCreate(RefundBase):
    """Schema để tạo Refund mới"""
    pass


class RefundUpdate(BaseModel):
    """Schema để cập nhật Refund"""
    amount: Optional[float] = Field(None, gt=0)
    reason: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = None


class RefundResponse(RefundBase):
    """Schema response cho Refund"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RefundListResponse(BaseModel):
    """Schema cho danh sách Refund với pagination"""
    total: int
    items: Sequence[RefundResponse]
    skip: int
    limit: int

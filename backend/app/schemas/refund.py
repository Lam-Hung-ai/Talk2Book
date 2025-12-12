# app/schemas/refund.py
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import RefundStatus


class RefundRead(BaseModel):
    """Schema để đọc thông tin Refund"""
    id: UUID
    booking_id: UUID
    amount: Decimal
    reason: str | None = None
    status: RefundStatus
    created_at: datetime

    class Config:
        from_attributes = True


class RefundCreate(BaseModel):
    """Schema để tạo Refund mới"""
    booking_id: UUID = Field(..., description="ID của booking cần hoàn tiền")
    amount: Decimal = Field(..., gt=0, description="Số tiền hoàn lại")
    reason: str | None = Field(default=None, description="Lý do hoàn tiền")
    status: RefundStatus = Field(default=RefundStatus.pending, description="Trạng thái refund")


class RefundUpdate(BaseModel):
    """Schema để cập nhật Refund"""
    amount: Decimal | None = Field(default=None, gt=0, description="Số tiền hoàn lại")
    reason: str | None = Field(default=None, description="Lý do hoàn tiền")
    status: RefundStatus | None = Field(default=None, description="Trạng thái refund")

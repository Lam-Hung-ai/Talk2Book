# app/schemas/support_ticket.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import SupportStatus


class SupportTicketBase(BaseModel):
    """Base schema cho SupportTicket"""
    user_id: UUID
    booking_id: UUID | None = Field(None, description="ID của booking liên quan (nếu có)")
    subject: str = Field(..., min_length=1, max_length=500, description="Tiêu đề ticket")
    status: SupportStatus = Field(default=SupportStatus.open, description="Trạng thái ticket")


class SupportTicketCreate(SupportTicketBase):
    """Schema để tạo SupportTicket mới"""
    pass


class SupportTicketUpdate(BaseModel):
    """Schema để cập nhật SupportTicket"""
    subject: str | None = Field(None, min_length=1, max_length=500)
    status: SupportStatus | None = None
    booking_id: UUID | None = None


class SupportTicketRead(SupportTicketBase):
    """Schema response cho SupportTicket"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


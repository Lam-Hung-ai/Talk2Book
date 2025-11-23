from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    """Base schema cho Review"""
    user_id: UUID
    service_type: str = Field(..., description="Loại dịch vụ: flight, hotel, tour, etc.")
    service_id: int | None = Field(None, description="ID của dịch vụ được đánh giá")
    rating: int = Field(..., ge=1, le=5, description="Đánh giá từ 1-5 sao")
    title: str = Field(..., min_length=1, max_length=200, description="Tiêu đề đánh giá")
    content: str = Field(..., min_length=1, description="Nội dung đánh giá")


class ReviewCreate(ReviewBase):
    """Schema để tạo Review mới"""
    pass


class ReviewUpdate(BaseModel):
    """Schema để cập nhật Review"""
    service_type: str | None = None
    service_id: int | None = None
    rating: int | None = Field(None, ge=1, le=5)
    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, min_length=1)


class ReviewResponse(ReviewBase):
    """Schema response cho Review"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """Schema cho danh sách Review với pagination"""
    total: int
    items: Sequence[ReviewResponse]
    skip: int
    limit: int
    average_rating: float | None = None

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ReviewTargetType


class ReviewBase(BaseModel):
    """Base schema cho Review"""
    user_id: UUID
    target_type: ReviewTargetType = Field(..., description="Loại đối tượng: hotel, product, flight, airport")
    target_key: str = Field(..., description="Key của đối tượng được đánh giá")
    rating: int = Field(..., ge=1, le=5, description="Đánh giá từ 1-5 sao")
    comment: str | None = Field(None, description="Bình luận đánh giá")


class ReviewCreate(ReviewBase):
    """Schema để tạo Review mới"""
    pass


class ReviewUpdate(BaseModel):
    """Schema để cập nhật Review"""
    target_type: ReviewTargetType | None = None
    target_key: str | None = None
    rating: int | None = Field(None, ge=1, le=5)
    comment: str | None = None


class ReviewRead(ReviewBase):
    """Schema response cho Review"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """Schema cho danh sách Review với pagination"""
    total: int
    items: Sequence[ReviewRead]
    skip: int
    limit: int
    average_rating: float | None = None

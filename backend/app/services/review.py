# app/services/review.py
from collections.abc import Sequence
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.review import Review
from app.repositories.review import ReviewRepository
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate


class ReviewService:
    """Service layer cho Review business logic"""

    def __init__(self, db: AsyncSession):
        self.repo = ReviewRepository(db)

    async def create_review(self, review_data: ReviewCreate) -> Review:
        """Tạo review mới"""
        # Validate rating
        if review_data.rating < 1 or review_data.rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )

        return await self.repo.create(review_data)

    async def get_review(self, review_id: UUID) -> Review:
        """Lấy review theo ID"""
        return await self.repo.get_or_404(review_id, detail="Review not found")

    async def get_reviews(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Review]:
        """Lấy danh sách tất cả reviews"""
        return await self.repo.get_multi(skip=skip, limit=limit)

    async def get_user_reviews(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Review]:
        """Lấy reviews của user"""
        return await self.repo.get_by_user_id(user_id, skip=skip, limit=limit)

    async def get_target_reviews(
        self,
        target_type: str,
        target_key: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Review]:
        """Lấy reviews của một đối tượng"""
        return await self.repo.get_by_target(
            target_type=target_type,
            target_key=target_key,
            skip=skip,
            limit=limit
        )

    async def get_reviews_by_rating(
        self,
        rating: int,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Review]:
        """Lấy reviews theo rating"""
        if rating < 1 or rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        return await self.repo.get_by_rating(rating, skip=skip, limit=limit)

    async def update_review(
        self,
        review_id: UUID,
        review_data: ReviewUpdate
    ) -> Review:
        """Cập nhật review"""
        review = await self.repo.get_or_404(review_id, detail="Review not found")

        # Validate rating nếu có update
        if review_data.rating is not None:
            if review_data.rating < 1 or review_data.rating > 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rating must be between 1 and 5"
                )

        return await self.repo.update(review, review_data)

    async def delete_review(self, review_id: UUID) -> None:
        """Xóa review"""
        await self.repo.delete(review_id)

    async def search_reviews(
        self,
        query: str,
        search_fields: list[str] | None = None,
        skip: int = 0,
        limit: int = 20
    ) -> Sequence[Review]:
        """Tìm kiếm reviews"""
        if search_fields is None:
            search_fields = ["comment", "target_key"]

        return await self.repo.search(
            query=query,
            search_columns=search_fields,
            skip=skip,
            limit=limit
        )

    async def get_target_review_stats(
        self,
        target_type: str,
        target_key: str
    ) -> dict[str, Any]:
        """Lấy thống kê reviews của một đối tượng"""
        total_reviews = await self.repo.count_by_target(target_type, target_key)
        average_rating = await self.repo.get_average_rating_by_target(target_type, target_key)
        rating_distribution = await self.repo.get_rating_distribution_by_target(
            target_type,
            target_key
        )

        return {
            "target_type": target_type,
            "target_key": target_key,
            "total_reviews": total_reviews,
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution
        }

    async def get_recent_reviews(
        self,
        target_type: str | None = None,
        limit: int = 10
    ) -> Sequence[Review]:
        """Lấy reviews mới nhất"""
        return await self.repo.get_recent_reviews(target_type=target_type, limit=limit)

    async def get_reviews_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        target_type: str | None = None,
        user_id: UUID | None = None
    ) -> dict[str, Any]:
        """Lấy danh sách reviews có phân trang và filter"""
        skip = (page - 1) * page_size

        filters = {}
        if target_type is not None:
            filters["target_type"] = target_type
        if user_id is not None:
            filters["user_id"] = user_id

        reviews = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [ReviewRead.model_validate(r, from_attributes=True) for r in reviews],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

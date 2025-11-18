# app/services/review.py
from typing import Optional, Sequence
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

from app.repositories.review import ReviewRepository
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.models.review_model import Review


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
    
    async def get_review(self, review_id: int) -> Review:
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
    
    async def get_service_reviews(
        self,
        service_type: str,
        service_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Review]:
        """Lấy reviews của một dịch vụ"""
        return await self.repo.get_by_service(
            service_type=service_type,
            service_id=service_id,
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
        review_id: int, 
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
    
    async def delete_review(self, review_id: int) -> None:
        """Xóa review"""
        await self.repo.delete(review_id)
    
    async def search_reviews(
        self,
        query: str,
        search_fields: Optional[list[str]] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Sequence[Review]:
        """Tìm kiếm reviews"""
        if search_fields is None:
            search_fields = ["title", "content", "service_type"]
        
        return await self.repo.search(
            query=query,
            search_columns=search_fields,
            skip=skip,
            limit=limit
        )
    
    async def get_service_review_stats(
        self,
        service_type: str,
        service_id: int
    ) -> dict:
        """Lấy thống kê reviews của một dịch vụ"""
        total_reviews = await self.repo.count_by_service(service_type, service_id)
        average_rating = await self.repo.get_average_rating_by_service(service_type, service_id)
        rating_distribution = await self.repo.get_rating_distribution_by_service(
            service_type, 
            service_id
        )
        
        return {
            "service_type": service_type,
            "service_id": service_id,
            "total_reviews": total_reviews,
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution
        }
    
    async def get_recent_reviews(
        self,
        service_type: Optional[str] = None,
        limit: int = 10
    ) -> Sequence[Review]:
        """Lấy reviews mới nhất"""
        return await self.repo.get_recent_reviews(service_type=service_type, limit=limit)

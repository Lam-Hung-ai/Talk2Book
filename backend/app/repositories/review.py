# app/repositories/review.py
from typing import Optional, Sequence
from uuid import UUID
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.review_model import Review
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository


class ReviewRepository(BaseCRUD[Review, ReviewCreate, ReviewUpdate], SearchableRepository[Review]):
    """Repository cho Review với đầy đủ CRUD và tính năng tìm kiếm"""
    
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, Review, db)
        SearchableRepository.__init__(self, Review, db)
    
    async def get_by_user_id(
        self, 
        user_id: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> Sequence[Review]:
        """Lấy danh sách reviews của một user"""
        return await self.get_multi(skip=skip, limit=limit, user_id=user_id)
    
    async def get_by_service(
        self,
        service_type: str,
        service_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Review]:
        """Lấy reviews của một dịch vụ cụ thể"""
        statement = select(Review).where(
            Review.service_type == service_type,
            Review.service_id == service_id
        ).offset(skip).limit(limit)
        result = await self.db.exec(statement)
        return result.all()
    
    async def get_by_service_type(
        self,
        service_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Review]:
        """Lấy reviews theo loại dịch vụ"""
        return await self.get_multi(skip=skip, limit=limit, service_type=service_type)
    
    async def get_by_rating(
        self,
        rating: int,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Review]:
        """Lấy reviews theo rating"""
        return await self.get_multi(skip=skip, limit=limit, rating=rating)
    
    async def get_by_rating_range(
        self,
        min_rating: int,
        max_rating: int,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Review]:
        """Lấy reviews trong khoảng rating"""
        statement = select(Review).where(
            Review.rating >= min_rating,
            Review.rating <= max_rating
        ).offset(skip).limit(limit)
        result = await self.db.exec(statement)
        return result.all()
    
    async def count_by_user_id(self, user_id: UUID) -> int:
        """Đếm số lượng reviews của user"""
        return await self.get_count(user_id=user_id)
    
    async def count_by_service(self, service_type: str, service_id: int) -> int:
        """Đếm số reviews của một dịch vụ"""
        statement = select(func.count()).select_from(Review).where(
            Review.service_type == service_type,
            Review.service_id == service_id
        )
        result = await self.db.exec(statement)
        return result.one()
    
    async def get_average_rating_by_service(
        self,
        service_type: str,
        service_id: int
    ) -> float:
        """Tính rating trung bình của một dịch vụ"""
        statement = select(func.avg(Review.rating)).where(
            Review.service_type == service_type,
            Review.service_id == service_id
        )
        result = await self.db.exec(statement)
        avg = result.one()
        return float(avg) if avg else 0.0
    
    async def get_rating_distribution_by_service(
        self,
        service_type: str,
        service_id: int
    ) -> dict:
        """Lấy phân bố rating của một dịch vụ (1-5 sao)"""
        distribution = {}
        for rating in range(1, 6):
            count_statement = select(func.count()).select_from(Review).where(
                Review.service_type == service_type,
                Review.service_id == service_id,
                Review.rating == rating
            )
            result = await self.db.exec(count_statement)
            distribution[f"{rating}_star"] = result.one()
        return distribution
    
    async def get_recent_reviews(
        self,
        service_type: Optional[str] = None,
        limit: int = 10
    ) -> Sequence[Review]:
        """Lấy reviews mới nhất"""
        from sqlmodel import desc
        
        statement = select(Review).order_by(desc(Review.created_at)).limit(limit)
        
        if service_type:
            statement = statement.where(Review.service_type == service_type)
        
        result = await self.db.exec(statement)
        return result.all()

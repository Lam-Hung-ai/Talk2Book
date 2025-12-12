# app/repositories/review.py
from collections.abc import Sequence
from uuid import UUID

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.review import Review
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.review import ReviewCreate, ReviewUpdate


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

    async def get_by_target(
        self,
        target_type: str,
        target_key: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Review]:
        """Lấy reviews của một đối tượng cụ thể"""
        statement = select(Review).where(
            Review.target_type == target_type,
            Review.target_key == target_key
        ).offset(skip).limit(limit)
        result = await self.db.exec(statement)
        return result.all()

    async def get_by_target_type(
        self,
        target_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Review]:
        """Lấy reviews theo loại đối tượng"""
        return await self.get_multi(skip=skip, limit=limit, target_type=target_type)

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

    async def count_by_target(self, target_type: str, target_key: str) -> int:
        """Đếm số reviews của một đối tượng"""
        statement = select(func.count()).select_from(Review).where(
            Review.target_type == target_type,
            Review.target_key == target_key
        )
        result = await self.db.exec(statement)
        return result.one()

    async def get_average_rating_by_target(
        self,
        target_type: str,
        target_key: str
    ) -> float:
        """Tính rating trung bình của một đối tượng"""
        statement = select(func.avg(Review.rating)).where(
            Review.target_type == target_type,
            Review.target_key == target_key
        )
        result = await self.db.exec(statement)
        avg = result.one()
        return float(avg) if avg else 0.0

    async def get_rating_distribution_by_target(
        self,
        target_type: str,
        target_key: str
    ) -> dict:
        """Lấy phân bố rating của một đối tượng (1-5 sao)"""
        distribution = {}
        for rating in range(1, 6):
            count_statement = select(func.count()).select_from(Review).where(
                Review.target_type == target_type,
                Review.target_key == target_key,
                Review.rating == rating
            )
            result = await self.db.exec(count_statement)
            distribution[f"{rating}_star"] = result.one()
        return distribution

    async def get_recent_reviews(
        self,
        target_type: str | None = None,
        limit: int = 10
    ) -> Sequence[Review]:
        """Lấy reviews mới nhất"""
        from sqlmodel import desc

        statement = select(Review).order_by(desc(Review.created_at)).limit(limit)

        if target_type:
            statement = statement.where(Review.target_type == target_type)

        result = await self.db.exec(statement)
        return result.all()

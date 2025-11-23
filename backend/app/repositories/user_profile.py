from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user_profile import UserProfile
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.user_profile import UserProfileCreate, UserProfileUpdate


class UserProfileRepository(
    BaseCRUD[UserProfile, UserProfileCreate, UserProfileUpdate],
    SearchableRepository[UserProfile]
):
    def __init__(self, db: AsyncSession):
        super().__init__(UserProfile, db)
        # Khởi tạo SearchableRepository với model UserProfile
        SearchableRepository.__init__(self, UserProfile, db)

    async def get_by_user_id(self, user_id: UUID) -> UserProfile | None:
        """Hàm riêng để tìm profile theo user_id (One-to-One)"""
        statement = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await self.db.exec(statement)
        return result.first()

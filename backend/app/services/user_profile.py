from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user_profile import UserProfile
from app.repositories.user_profile import UserProfileRepository
from app.schemas.user_profile import UserProfileCreate, UserProfileUpdate


class UserProfileService:
    def __init__(self, db: AsyncSession):
        self.repo = UserProfileRepository(db)

    async def create_profile(self, profile_in: UserProfileCreate) -> UserProfile:
        # Logic kiểm tra: 1 User chỉ được có 1 Profile
        existing_profile = await self.repo.get_by_user_id(profile_in.user_id)
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User này đã có hồ sơ (Profile)"
            )
        return await self.repo.create(profile_in)

    async def get_profile(self, profile_id: UUID) -> UserProfile:
        return await self.repo.get_or_404(profile_id, detail="Hồ sơ không tồn tại")

    async def get_profile_by_user_id(self, user_id: UUID) -> UserProfile:
        profile = await self.repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User chưa cập nhật hồ sơ")
        return profile

    async def update_profile(self, profile_id: UUID, profile_in: UserProfileUpdate) -> UserProfile:
        db_profile = await self.get_profile(profile_id)

        # Tự động cập nhật thời gian updated_at
        update_data = profile_in.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now(UTC)

        return await self.repo.update(db_profile, update_data)

    async def delete_profile(self, profile_id: UUID) -> None:
        await self.repo.delete(profile_id)

    async def get_profiles_paginated(self, page: int, page_size: int):
        skip = (page - 1) * page_size
        profiles = await self.repo.get_multi(skip=skip, limit=page_size)
        total = await self.repo.get_count()
        return {"data": profiles, "total": total, "page": page, "page_size": page_size}

    async def search_profiles(
            self, q: str, page: int, page_size: int, exact_match: bool, case_sensitive: bool
    ):
        skip = (page - 1) * page_size
        # Chỉ định các cột cho phép tìm kiếm
        search_columns = ["full_name", "address", "nationality"]

        results = await self.repo.search(
            query=q,
            search_columns=search_columns,
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size
        )
        return {"data": results, "page": page, "page_size": page_size}

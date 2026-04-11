# app/services/user.py
from typing import Any

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import UserProfile
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.role import RoleEnum
from app.schemas.user import AllUserInfor, UserRead
from app.services.role import RoleService


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)
        self.role_service = RoleService(db)
        self.db = db

    async def get_user_by_id(self, user_id: str) -> User:
        return await self.repo.get_or_404(user_id, detail="User không tồn tại")

    async def add_role(self, user_id: str, role: RoleEnum) -> None:
        user: User = await self.get_user_by_id(user_id)
        await self.db.refresh(user, ["roles"])
        default_role = await self.role_service.role_repo.get_by_code(role)

        if default_role is None:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Cannot find default role",
            )
        user.roles = [default_role]
        self.db.add(user)
        await self.db.commit()

    async def get_all_info_by_id(self, user_id: str) -> AllUserInfor:
        user: User = await self.repo.get_or_404(user_id, detail="User không tồn tại")

        await self.db.refresh(user, ["roles", "user_profile"])

        user_roles: list[str] = []
        if user.roles is not None:
            user_roles = [r.code for r in user.roles]

        user_profile: UserProfile | None = user.user_profile

        return AllUserInfor(
            user_id=user.id,
            name=user.name,
            email=str(user.email),
            email_verified=user.email_verified,
            image=user.image,
            created_at=user.created_at,
            updated_at=user.updated_at,
            full_name=user_profile.full_name if user_profile else None,
            gender=user_profile.gender if user_profile else None,
            birthday=user_profile.birthday if user_profile else None,
            nationality=user_profile.nationality if user_profile else None,
            avatar_url=user_profile.avatar_url if user_profile else None,
            address=user_profile.address if user_profile else None,
            profile_updated_at=user_profile.updated_at if user_profile else None,
            roles=user_roles,
        )

    async def get_users_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size

        users = await self.repo.get_multi(skip=skip, limit=page_size)
        total = await self.repo.get_count()

        return {
            "items": [UserRead.model_validate(u, from_attributes=True) for u in users],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def delete_user(self, user_id: str) -> None:
        await self.repo.delete(user_id)

    async def search_users(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size

        users = await self.repo.search(
            query=q,
            search_columns=["email", "name"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )

        total = await self.repo.count_search(
            query=q,
            search_columns=["email", "name"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [UserRead.model_validate(u, from_attributes=True) for u in users],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

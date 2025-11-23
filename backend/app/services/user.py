# app/services/user.py
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import hash_password
from app.models import UserProfile
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.role import RoleEnum
from app.schemas.user import AllUserInfor, UserCreate, UserRead
from app.services.role import RoleService


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)
        self.role_service = RoleService(db)
        self.db = db

    async def get_user_by_id(self, user_id: UUID) -> User:
        """Lấy user theo ID, ném 404 nếu không tồn tại"""
        return await self.repo.get_or_404(user_id, detail="User không tồn tại")

    async def add_role(self, user_id: UUID, role: RoleEnum) -> None:
        user: User = await self.get_user_by_id(user_id)
        await self.db.refresh(user, ["roles"])
        default_role = await self.role_service.role_repo.get_by_code(role)

        if default_role is None:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Cannot find default role")
        user.roles = [default_role]
        self.db.add(user)
        await self.db.commit()


    async def create_user(self, user_in: UserCreate) -> UserRead:
        """Tạo user mới"""
        if await self.repo.get_by_email(str(user_in.email)):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email has existed")

        if await self.repo.get_by_phone(user_in.phone):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone has existed")

        password_hash = hash_password(user_in.password)
        user_data = user_in.model_dump()
        user_data.pop("password")
        user_data["password_hash"] = password_hash

        db_user = await self.repo.create(user_data)
        user = UserRead.model_validate(db_user, from_attributes=True)
        await self.add_role(user_id=user.id, role=RoleEnum.user)
        return user


    async def get_all_info_by_id(self, user_id: UUID) -> AllUserInfor:
        # get info from user table
        user:  User = await self.repo.get_or_404(user_id, detail="User không tồn tại")


        await self.db.refresh(user, ["roles", "user_profile"])

        user_roles = []
        if user.roles is not None:
            user_roles: list[str] = [r.code for r in user.roles]

        user_profile: UserProfile | None = user.user_profile

        profile_data = (
            user_profile.model_dump(exclude={"user_id"})
            if user_profile is not None
            else {}
        )

        user_info = AllUserInfor(
            user_id=user.id,
            email=str(user.email),
            phone=user.phone,
            status=user.status,
            created_at=user.created_at,
            roles=user_roles,
            **profile_data
        )

        return user_info

    async def get_users_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        is_active: bool | None = None
    ) -> dict[str, Any]:
        """Lấy danh sách users có phân trang và filter"""
        skip = (page - 1) * page_size

        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active

        users = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [UserRead.model_validate(u, from_attributes=True) for u in users],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def delete_user(self, user_id: UUID) -> None:
        """Xóa user"""
        await self.repo.delete(user_id)

    async def search_users(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False
    ) -> dict[str, Any]:
        """Tìm kiếm users theo email hoặc full_name"""
        skip = (page - 1) * page_size

        users = await self.repo.search(
            query=q,
            search_columns=["email", "phone"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size
        )

        total = await self.repo.count_search(
            query=q,
            search_columns=["email", "phone"],
            exact_match=exact_match,
            case_sensitive=case_sensitive
        )

        return {
            "items": [UserRead.model_validate(u, from_attributes=True) for u in users],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

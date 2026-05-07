# app/services/role.py
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.repositories.user_role import UserRoleRepository
from app.schemas.role import RoleCreate, RoleRead, RoleUpdate
from app.schemas.user import UserRead
from app.schemas.user_role import UserRoleRead


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_repo = RoleRepository(db)
        self.user_role_repo = UserRoleRepository(db)
        self.user_repo = UserRepository(db)

    # --------- CRUD ROLE ---------
    async def create_role(self, role_in: RoleCreate) -> RoleRead:
        if await self.role_repo.get_by_code(role_in.code):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role code đã tồn tại",
            )

        db_role = await self.role_repo.create(role_in)
        return RoleRead.model_validate(db_role, from_attributes=True)

    async def get_role(self, role_id: UUID) -> RoleRead:
        db_role = await self.role_repo.get_or_404(role_id, detail="Role không tồn tại")
        return RoleRead.model_validate(db_role, from_attributes=True)

    async def get_roles_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size
        roles = await self.role_repo.get_multi(skip=skip, limit=page_size)
        total = await self.role_repo.get_count()

        return {
            "items": [RoleRead.model_validate(r, from_attributes=True) for r in roles],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_role(self, role_id: UUID, role_in: RoleUpdate) -> RoleRead:
        db_role = await self.role_repo.get_or_404(role_id, detail="Role không tồn tại")

        # Nếu client update code, kiểm tra trùng
        if role_in.code is not None and role_in.code != db_role.code:
            if await self.role_repo.get_by_code(role_in.code):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Role code đã tồn tại",
                )

        updated = await self.role_repo.update(db_role, role_in)
        return RoleRead.model_validate(updated, from_attributes=True)

    async def delete_role(self, role_id: UUID) -> None:
        await self.role_repo.delete(role_id)

    # --------- USER-ROLE MAPPING ---------
    async def assign_role_to_user(self, user_id: str, role_id: UUID) -> UserRoleRead:
        # đảm bảo user & role tồn tại
        await self.user_repo.get_or_404(user_id, detail="User không tồn tại")
        await self.role_repo.get_or_404(role_id, detail="Role không tồn tại")

        user_role = await self.user_role_repo.add_role_to_user(user_id, role_id)
        return UserRoleRead.model_validate(user_role, from_attributes=True)

    async def remove_role_from_user(self, user_id: str, role_id: UUID) -> None:
        await self.user_role_repo.remove_role_from_user(user_id, role_id)

    async def get_roles_of_user(self, user_id: str) -> list[RoleRead]:
        await self.user_repo.get_or_404(user_id, detail="User không tồn tại")
        roles = await self.user_role_repo.get_roles_for_user(user_id)
        return [RoleRead.model_validate(r, from_attributes=True) for r in roles]

    async def get_users_of_role(self, role_id: UUID) -> list[UserRead]:
        await self.role_repo.get_or_404(role_id, detail="Role không tồn tại")
        users = await self.user_role_repo.get_users_for_role(role_id)
        return [UserRead.model_validate(u, from_attributes=True) for u in users]

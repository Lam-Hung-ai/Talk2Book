# app/repositories/user_role_repository.pySequence
from collections.abc import Sequence
from uuid import UUID

from sqlmodel import and_, col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole


class UserRoleRepository:
    """
    Repository cho bảng mapping UserRole (user_id <-> role_id)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_role_to_user(self, user_id: UUID, role_id: UUID) -> UserRole:
        """
        Gán 1 role cho user. Nếu đã tồn tại thì giữ nguyên.
        """
        result = await self.db.exec(
            select(UserRole).where(
                and_(UserRole.user_id == user_id,
                UserRole.role_id == role_id)
                )
        )
        user_role = result.first()
        if user_role:
            return user_role

        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(user_role)
        await self.db.commit()
        await self.db.refresh(user_role)
        return user_role

    async def remove_role_from_user(self, user_id: UUID, role_id: UUID) -> None:
        """
        Bỏ gán 1 role khỏi user
        """
        await self.db.exec(
            delete(UserRole).where(
                and_(UserRole.user_id == user_id,
                UserRole.role_id == role_id)
            )
        )
        await self.db.commit()

    async def remove_all_roles_for_user(self, user_id: UUID) -> int:
        """
        Xóa toàn bộ role của 1 user. Trả về số bản ghi đã xóa.
        """
        result = await self.db.exec(
            select(UserRole).where(UserRole.user_id == user_id)
        )
        items = result.all()
        await self.db.exec(
            delete(UserRole).where(col(UserRole.user_id == user_id))
        )
        await self.db.commit()
        return len(items)

    async def get_roles_for_user(self, user_id: UUID) -> Sequence[Role]:
        """
        Lấy danh sách Role của 1 user
        """
        result = await self.db.exec(
            select(Role)
            .join(UserRole, col(UserRole.role_id == Role.id))
            .where(UserRole.user_id == user_id)
        )
        return result.all()

    async def get_users_for_role(self, role_id: UUID) -> Sequence[User]:
        """
        Lấy danh sách User của 1 role
        """
        result = await self.db.exec(
            select(User)
            .join(UserRole, col(UserRole.user_id == User.id))
            .where(UserRole.role_id == role_id)
        )
        return result.all()

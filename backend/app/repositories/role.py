# app/repositories/role.py

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.role import Role
from app.repositories.base import BaseCRUD
from app.schemas.role import RoleCreate, RoleUpdate


class RoleRepository(BaseCRUD[Role, RoleCreate, RoleUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Role, db)

    async def get_by_code(self, code: str) -> Role | None:
        result = await self.db.exec(select(Role).where(Role.code == code))
        return result.first()

# app/repositories/user_repository.py
from typing import Any

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.user import UserUpdate


class UserRepository(BaseCRUD[User, Any, UserUpdate], SearchableRepository):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, User, db)
        SearchableRepository.__init__(self, User, db)

    async def get_by_email(self, email: str) -> User | None:
        return (await self.db.exec(select(User).where(User.email == email))).first()

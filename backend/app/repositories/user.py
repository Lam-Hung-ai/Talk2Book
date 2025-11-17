# app/repositories/user_repository.py
from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository

class UserRepository(BaseCRUD[User, UserCreate, UserUpdate], SearchableRepository):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, User, db)
        SearchableRepository.__init__(self, User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Tìm user riêng theo email (index optimized)"""
        return ( await self.db.exec(select(User).where(User.email == email)) ).first()
    
    async def get_by_phone(self, phone: str) -> Optional[User]:
        """Tìm user riêng theo phone (index optimized)"""
        return ( await self.db.exec(select(User).where(User.phone == phone)) ).first()
    
    async def get_active_users(self, skip: int = 0, limit: int = 100):
        return self.get_multi(skip=skip, limit=limit, is_active=True)
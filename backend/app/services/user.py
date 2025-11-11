from typing import Optional, Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.user import User
from fastapi import HTTPException, status
from app.schemas.user import UserCreate, UserRead
from app.repositories.user import UserRepository
from app.core.security import hash_password

class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)
    
    async def create_user(self, user_in: UserCreate) -> UserRead:
        """Tạo user mới"""
        if await self.repo.get_by_email(user_in.email):
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
        
        db_user = self.repo.create(user_data)
        return UserRead.model_validate(db_user)
    
    async def get_user_by_id(self, user_id: int) -> User:
        """Lấy user theo ID, ném 404 nếu không tồn tại"""
        return await self.repo.get_or_404(user_id, detail="User không tồn tại")
    
    async def get_users_paginated(
        self, 
        page: int = 1, 
        page_size: int = 20,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Lấy danh sách users có phân trang và filter"""
        skip = (page - 1) * page_size
        
        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active
        
        users = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)
        
        return {
            "items": [UserRead.model_validate(u) for u in users],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    async def delete_user(self, user_id: int) -> None:
        """Xóa user"""
        await self.repo.delete(user_id)
    
    async def search_users(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False
    ) -> Dict[str, Any]:
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
            "items": [UserRead.model_validate(u) for u in users],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
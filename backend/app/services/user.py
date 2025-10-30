from sqlmodel import select, or_, and_, col
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence
from fastapi import HTTPException
from app.models.user import User, UserStatus
from app.core.sercurity import hash_password
from uuid import UUID

async def list_users(
    session: AsyncSession, 
    *, 
    limit: int, 
    offset: int, 
    q: str | None = None, 
    status: UserStatus | None = None
    ) -> tuple[Sequence[User], int]:
    
    statement = select(User)
    if q:
        pattern = f"%{q}%"
        statement = statement.where(or_(col(User.email).contains(pattern), col(User.phone).contains(pattern)))
    if status:
        statement = statement.where(User.status == status)
    users = await session.exec(statement.offset(offset).limit(limit))
    total_items = await session.exec(statement)
    return users.all(), len(total_items.all())

async def create_user(session: AsyncSession, *, email: str, phone: str, password: str) -> User:

    if (await session.exec(select(User).where(User.email == email))).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    if (await session.exec(select(User).where(User.phone == phone))).first():
        raise HTTPException(status_code=409, detail="Phone already exists")

    user = User(email=email, phone=phone, password_hash=hash_password(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def get_user(session: AsyncSession, user_id: UUID) -> User:
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def update_user(session: AsyncSession, 
                user_id: UUID, 
                *, 
                email: str | None, 
                phone: str | None, 
                password: str | None, 
                status: UserStatus | None) -> User:
    user = await get_user(session, user_id)
    if email and email != user.email:
        if (await session.exec(select(User).where(User.email == email))).first():
            raise HTTPException(status_code=409, detail="Email already exists")
        user.email = email
    if phone and phone != user.phone:
        if (await session.exec(select(User).where(User.phone == phone))).first():
            raise HTTPException(status_code=409, detail="Phone already exists")
        user.phone = phone
    if password:
        user.password_hash = hash_password(password)
    if status:
        user.status = status
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def soft_delete_user(session: AsyncSession, user_id: UUID) -> None:
    user = await get_user(session, user_id)
    user.status = UserStatus.deleted
    session.add(user)
    await session.commit()

async def hard_delete_user(session: AsyncSession, user_id: UUID) -> None:
    user = get_user(session, user_id)
    await session.delete(user)
    await session.commit()
    
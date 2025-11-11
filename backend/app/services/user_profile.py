from uuid import UUID

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user_profile import UserProfile
from app.schemas.user_profile import ProfileCreate, ProfileRead
from app.services.user import get_user


async def upsert_profile(session: AsyncSession, user_id: UUID, **kwargs) -> UserProfile:
    try:
        _ = await get_user(session, user_id) 
    except:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = (await session.exec(select(UserProfile).where(UserProfile.user_id == user_id))).first()

    if not profile:
        profile = UserProfile(user_id=user_id, **kwargs)
    else:
        for k, v in kwargs.items():
            setattr(profile, k, v)
            
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile

async def get_profile(session: AsyncSession, user_id: UUID) -> UserProfile:
    profile = ( await session.exec(select(UserProfile).where(UserProfile.user_id == user_id))).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
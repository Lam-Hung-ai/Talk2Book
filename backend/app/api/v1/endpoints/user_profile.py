from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.user_profile import ProfileCreate, ProfileRead
from app.services.user_profile import get_profile, upsert_profile

router = APIRouter(prefix="/users", tags=["users"])


@router.put("/{user_id}/profile", response_model=ProfileRead)
async def upsert_profile_ep(
    user_id: UUID,
    payload: ProfileCreate,
    session: AsyncSession = Depends(get_async_session),
):
    profile = await upsert_profile(
        session, user_id, **payload.model_dump(exclude_none=True)
    )
    return profile


@router.get("/{user_id}/profile", response_model=ProfileRead)
async def get_profile_ep(
    user_id: UUID, session: AsyncSession = Depends(get_async_session)
):
    return await get_profile(session, user_id)

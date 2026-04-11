from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.user_profile import (
    UserProfileCreate,
    UserProfileRead,
    UserProfileUpdate,
)
from app.services.user_profile import UserProfileService

router = APIRouter()


def get_profile_service(
    db: AsyncSession = Depends(get_async_session),
) -> UserProfileService:
    return UserProfileService(db)


@router.post(
    "/",
    response_model=UserProfileRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo hồ sơ người dùng mới",
)
async def create_user_profile(
    profile_in: UserProfileCreate,
    service: UserProfileService = Depends(get_profile_service),
):
    """
    Tạo profile cho user. Yêu cầu user_id chưa có profile.
    """
    return await service.create_profile(profile_in)


@router.get(
    "/{profile_id}",
    response_model=UserProfileRead,
    summary="Lấy thông tin hồ sơ theo ID",
)
async def get_user_profile(
    profile_id: UUID, service: UserProfileService = Depends(get_profile_service)
):
    return await service.get_profile(profile_id)


@router.get(
    "/user/{user_id}", response_model=UserProfileRead, summary="Lấy hồ sơ theo User ID"
)
async def get_profile_by_user(
    user_id: str, service: UserProfileService = Depends(get_profile_service)
):
    """
    Tiện ích để lấy profile dựa trên ID của User (thay vì ID của Profile)
    """
    return await service.get_profile_by_user_id(user_id)


@router.get("/", response_model=dict, summary="Danh sách hồ sơ (Admin)")
async def get_user_profiles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: UserProfileService = Depends(get_profile_service),
):
    return await service.get_profiles_paginated(page=page, page_size=page_size)


@router.put("/{profile_id}", response_model=UserProfileRead, summary="Cập nhật hồ sơ")
async def update_user_profile(
    profile_id: UUID,
    profile_in: UserProfileUpdate,
    service: UserProfileService = Depends(get_profile_service),
):
    return await service.update_profile(profile_id, profile_in)


@router.delete(
    "/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa hồ sơ"
)
async def delete_user_profile(
    profile_id: UUID, service: UserProfileService = Depends(get_profile_service)
):
    await service.delete_profile(profile_id)
    return None


@router.get("/search/mixin", response_model=dict, summary="Tìm kiếm hồ sơ")
async def search_user_profiles(
    q: str = Query(..., min_length=1, description="Tìm theo tên, địa chỉ, quốc tịch"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False),
    case_sensitive: bool = Query(False),
    service: UserProfileService = Depends(get_profile_service),
):
    """
    Tìm kiếm trong các cột: address, nationality
    """
    return await service.search_profiles(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )

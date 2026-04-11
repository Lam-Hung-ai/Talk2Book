# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.user import AllUserInfor, UserRead, UserUpdate
from app.services.user import UserService

router = APIRouter()


def get_user_service(db: AsyncSession = Depends(get_async_session)) -> UserService:
    return UserService(db)


@router.get(
    "/me",
    response_model=AllUserInfor,
    summary="Lấy thông tin user hiện đăng nhập",
)
async def get_current_user_info():
    """Gắn user_id từ Better Auth session / API gateway khi tích hợp."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Chưa gắn user_id từ Better Auth; dùng GET /user/all_user_info/{user_id} hoặc /user/{user_id}.",
    )


@router.get("/{user_id}", response_model=UserRead, summary="Lấy thông tin user theo ID")
async def get_user(user_id: str, service: UserService = Depends(get_user_service)):
    user = await service.get_user_by_id(user_id)
    return UserRead.model_validate(user, from_attributes=True)


@router.get("/", response_model=dict, summary="Danh sách users có phân trang")
async def get_users(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    service: UserService = Depends(get_user_service),
):
    return await service.get_users_paginated(page=page, page_size=page_size)


@router.get(
    "/all_user_info/{user_id}",
    response_model=AllUserInfor,
    summary="Chi tiết user (user + role + profile)",
)
async def get_detail_user_info_by_id(
    user_id: str, service: UserService = Depends(get_user_service)
):
    return await service.get_all_info_by_id(user_id)


@router.put("/{user_id}", response_model=UserRead, summary="Cập nhật thông tin user")
async def update_user(
    user_id: str, user_in: UserUpdate, service: UserService = Depends(get_user_service)
):
    db_user = await service.get_user_by_id(user_id)
    updated_user = await service.repo.update(db_user, user_in)
    return UserRead.model_validate(updated_user, from_attributes=True)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa user")
async def delete_user(user_id: str, service: UserService = Depends(get_user_service)):
    await service.delete_user(user_id)
    return None


@router.get(
    "/search/mixin",
    response_model=dict,
    summary="Tìm kiếm users theo email hoặc tên",
)
async def search_users(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: UserService = Depends(get_user_service),
):
    return await service.search_users(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )

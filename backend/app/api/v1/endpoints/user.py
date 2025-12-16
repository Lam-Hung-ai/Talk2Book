# app/api/v1/endpoints/users.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.user import AllUserInfor, UserCreate, UserRead, UserUpdate
from app.services.user import UserService

router = APIRouter()


def get_user_service(db: AsyncSession = Depends(get_async_session)) -> UserService:
    return UserService(db)


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo user mới",
    description="Tạo user mới, yêu cầu quyền admin",
)
async def create_user(
    user_in: UserCreate, service: UserService = Depends(get_user_service)
):
    """
    Endpoint tạo user mới với validation email unique
    """
    return await service.create_user(user_in)


@router.get("/{user_id}", response_model=UserRead, summary="Lấy thông tin user theo ID")
async def get_user(user_id: UUID, service: UserService = Depends(get_user_service)):
    """
    Lấy thông tin user theo ID. Ném 404 nếu không tồn tại
    """
    user = await service.get_user_by_id(user_id)
    return UserRead.model_validate(user, from_attributes=True)


@router.get("/", response_model=dict, summary="Danh sách users có phân trang")
async def get_users(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    is_active: bool | None = Query(None, description="Lọc theo trạng thái"),
    service: UserService = Depends(get_user_service),
):
    """
    Lấy danh sách users với phân trang và filter
    """
    return await service.get_users_paginated(
        page=page, page_size=page_size, is_active=is_active
    )


@router.get(
    "/all_user_info/{user_id}",
    response_model=AllUserInfor,
    summary="Lấy thông tin chi tiết của 1 người dùng gồm bảng user, role, userprofile",
)
async def get_detail_user_info_by_id(
    user_id: UUID, service: UserService = Depends(get_user_service)
):
    """
    Lấy thông tin user theo ID. Ném 404 nếu không tồn tại
    """
    user = await service.get_all_info_by_id(user_id)
    return AllUserInfor.model_validate(user, from_attributes=True)


@router.put("/{user_id}", response_model=UserRead, summary="Cập nhật thông tin user")
async def update_user(
    user_id: UUID, user_in: UserUpdate, service: UserService = Depends(get_user_service)
):
    """
    Cập nhật user. User chỉ được sửa thông tin của chính mình, trừ admin
    """
    # if current_user.id != user_id and not current_user.is_superuser:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Bạn không có quyền sửa thông tin này"
    #     )

    db_user = await service.get_user_by_id(user_id)
    updated_user = await service.repo.update(db_user, user_in)
    return UserRead.model_validate(updated_user, from_attributes=True)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa user")
async def delete_user(user_id: UUID, service: UserService = Depends(get_user_service)):
    """
    Xóa user (hard delete). Có thể đổi thành soft delete nếu cần
    """
    await service.delete_user(user_id)
    return None


@router.get(
    "/search/mixin", response_model=dict, summary="Tìm kiếm users theo email hoặc tên"
)
async def search_users(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: UserService = Depends(get_user_service),
):
    """
    Search users in both email and full_name columns

    Examples:
    - `/users/search/mixin?q=john` → tìm "john" trong email hoặc tên (không phân biệt hoa/thường)
    - `/users/search/mixin?q=John@example.com&exact_match=true` → tìm chính xác email
    - `/users/search/mixin?q=Alice&case_sensitive=true` → chỉ tìm "Alice" (viết hoa A)
    """
    return await service.search_users(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )


# ========== ME (Current User) ==========
# @router.get(
#     "/me",
#     response_model=UserRead,
#     summary="Lấy thông tin user hiện đăng nhập"
# )
# async def get_current_user_info(
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Lấy thông tin của user đang đăng nhập (từ JWT token)
#     """
#     return UserRead.model_validate(current_user, from_attributes=True)

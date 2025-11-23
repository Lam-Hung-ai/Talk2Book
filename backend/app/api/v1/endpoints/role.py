# app/api/v1/endpoints/roles.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.role import RoleCreate, RoleRead, RoleUpdate
from app.schemas.user import UserRead
from app.schemas.user_role import UserRoleRead
from app.services.role import RoleService

router = APIRouter()


def get_role_service(db: AsyncSession = Depends(get_async_session)) -> RoleService:
    return RoleService(db)


@router.post(
    "/",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo role mới",
)
async def create_role(
    role_in: RoleCreate,
    service: RoleService = Depends(get_role_service),
):
    return await service.create_role(role_in)


@router.get(
    "/{role_id}",
    response_model=RoleRead,
    summary="Lấy thông tin role theo ID",
)
async def get_role(
    role_id: UUID,
    service: RoleService = Depends(get_role_service),
):
    return await service.get_role(role_id)


@router.get(
    "/",
    response_model=dict,
    summary="Danh sách roles có phân trang",
)
async def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    service: RoleService = Depends(get_role_service),
):
    return await service.get_roles_paginated(page=page, page_size=page_size)


@router.put(
    "/{role_id}",
    response_model=RoleRead,
    summary="Cập nhật role",
)
async def update_role(
    role_id: UUID,
    role_in: RoleUpdate,
    service: RoleService = Depends(get_role_service),
):
    return await service.update_role(role_id, role_in)


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa role",
)
async def delete_role(
    role_id: UUID,
    service: RoleService = Depends(get_role_service),
):
    await service.delete_role(role_id)
    return None


# ---------- USER-ROLE MAPPING ----------


@router.post(
    "/{role_id}/users/{user_id}",
    response_model=UserRoleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Gán role cho user",
)
async def assign_role_to_user(
    role_id: UUID,
    user_id: UUID,
    service: RoleService = Depends(get_role_service),
):
    return await service.assign_role_to_user(user_id=user_id, role_id=role_id)


@router.delete(
    "/{role_id}/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Bỏ gán role khỏi user",
)
async def remove_role_from_user(
    role_id: UUID,
    user_id: UUID,
    service: RoleService = Depends(get_role_service),
):
    await service.remove_role_from_user(user_id=user_id, role_id=role_id)
    return None


@router.get(
    "/user/{user_id}",
    response_model=list[RoleRead],
    summary="Lấy danh sách role của 1 user",
)
async def get_roles_of_user(
    user_id: UUID,
    service: RoleService = Depends(get_role_service),
):
    return await service.get_roles_of_user(user_id)


@router.get(
    "/{role_id}/users",
    response_model=list[UserRead],
    summary="Lấy danh sách user của 1 role",
)
async def get_users_of_role(
    role_id: UUID,
    service: RoleService = Depends(get_role_service),
):
    return await service.get_users_of_role(role_id)

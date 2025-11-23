# app/api/v1/endpoints/refresh_token.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.refresh_token import (
    RefreshTokenCreate,
    RefreshTokenRead,
    RefreshTokenUpdate,
)
from app.services.refresh_token import RefreshTokenService

router = APIRouter()


def get_refresh_token_service(
    db: AsyncSession = Depends(get_async_session),
) -> RefreshTokenService:
    return RefreshTokenService(db)


@router.post(
    "/",
    response_model=RefreshTokenRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo refresh token mới",
)
async def create_refresh_token(
    token_in: RefreshTokenCreate,
    service: RefreshTokenService = Depends(get_refresh_token_service),
):
    # Thực tế thường sẽ tạo token trong flow login / rotate token,
    # ở đây chỉ là CRUD thuần để bạn test.
    return await service.create_refresh_token(token_in)


@router.get(
    "/{jti}",
    response_model=RefreshTokenRead,
    summary="Lấy thông tin refresh token theo jti",
)
async def get_refresh_token(
    jti: UUID,
    service: RefreshTokenService = Depends(get_refresh_token_service),
):
    return await service.get_by_jti(jti)


@router.get(
    "/user/{user_id}",
    response_model=list[RefreshTokenRead],
    summary="Lấy danh sách refresh token của 1 user",
)
async def get_user_tokens(
    user_id: UUID,
    include_revoked: bool = Query(
        False, description="Có lấy luôn token đã revoked hay không"
    ),
    service: RefreshTokenService = Depends(get_refresh_token_service),
):
    return await service.get_user_tokens(user_id, include_revoked)


@router.post(
    "/{jti}/revoke",
    response_model=RefreshTokenRead,
    summary="Revoke 1 refresh token theo jti",
)
async def revoke_refresh_token(
    jti: UUID,
    service: RefreshTokenService = Depends(get_refresh_token_service),
):
    return await service.revoke_token(jti)


@router.post(
    "/user/{user_id}/revoke-all",
    summary="Revoke toàn bộ refresh token còn sống của 1 user",
)
async def revoke_all_user_tokens(
    user_id: UUID,
    service: RefreshTokenService = Depends(get_refresh_token_service),
):
    return await service.revoke_all_for_user(user_id)


@router.put(
    "/{jti}",
    response_model=RefreshTokenRead,
    summary="Cập nhật refresh token (revoked, expires_at, ...)",
)
async def update_refresh_token(
    jti: UUID,
    token_in: RefreshTokenUpdate,
    service: RefreshTokenService = Depends(get_refresh_token_service),
):
    return await service.update_refresh_token(jti, token_in)


@router.delete(
    "/{jti}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa refresh token theo jti",
)
async def delete_refresh_token(
    jti: UUID,
    service: RefreshTokenService = Depends(get_refresh_token_service),
):
    await service.delete_refresh_token(jti)
    return None


@router.delete(
    "/expired",
    summary="Xóa tất cả refresh token đã hết hạn",
)
async def delete_expired_tokens(
    service: RefreshTokenService = Depends(get_refresh_token_service),
):
    return await service.delete_expired()

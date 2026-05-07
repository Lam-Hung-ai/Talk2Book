# app/api/v1/endpoints/provider.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.provider import ProviderCreate, ProviderRead, ProviderUpdate
from app.services.provider import ProviderService

router = APIRouter()


def get_provider_service(
    db: AsyncSession = Depends(get_async_session),
) -> ProviderService:
    return ProviderService(db)


@router.post(
    "/",
    response_model=ProviderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo provider mới",
)
async def create_provider(
    provider_in: ProviderCreate,
    service: ProviderService = Depends(get_provider_service),
):
    return await service.create_provider(provider_in)


@router.get(
    "/",
    response_model=dict,
    summary="Danh sách provider có phân trang",
)
async def list_providers(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    type_filter: str | None = Query(None, description="Lọc theo type"),
    country_code: str | None = Query(None, description="Lọc theo country_code"),
    status_filter: str | None = Query(None, description="Lọc theo status"),
    service: ProviderService = Depends(get_provider_service),
):
    return await service.get_providers_paginated(
        page=page,
        page_size=page_size,
        type_filter=type_filter,
        country_code=country_code,
        status_filter=status_filter,
    )


@router.get(
    "/search",
    response_model=dict,
    summary="Tìm kiếm provider theo tên/địa lý",
)
async def search_providers(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: ProviderService = Depends(get_provider_service),
):
    return await service.search_providers(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )


@router.get(
    "/{provider_id}",
    response_model=ProviderRead,
    summary="Lấy thông tin provider theo ID",
)
async def get_provider(
    provider_id: UUID, service: ProviderService = Depends(get_provider_service)
):
    return await service.get_provider(provider_id)


@router.put(
    "/{provider_id}",
    response_model=ProviderRead,
    summary="Cập nhật provider",
)
async def update_provider(
    provider_id: UUID,
    provider_in: ProviderUpdate,
    service: ProviderService = Depends(get_provider_service),
):
    return await service.update_provider(provider_id, provider_in)


@router.delete(
    "/{provider_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa provider",
)
async def delete_provider(
    provider_id: UUID, service: ProviderService = Depends(get_provider_service)
):
    await service.delete_provider(provider_id)
    return None

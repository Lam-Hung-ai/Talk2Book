# app/api/v1/endpoints/country.py
from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.country import CountryCreate, CountryRead, CountryUpdate
from app.services.country import CountryService

router = APIRouter()


def get_country_service(
    db: AsyncSession = Depends(get_async_session),
) -> CountryService:
    return CountryService(db)


@router.post(
    "/",
    response_model=CountryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo country mới",
    description="Tạo country mới với code, name và currency_code",
)
async def create_country(
    country_in: CountryCreate, service: CountryService = Depends(get_country_service)
):
    """
    Endpoint tạo country mới với validation code unique
    """
    return await service.create_country(country_in)


@router.get("/", response_model=dict, summary="Danh sách countries có phân trang")
async def get_countries(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    service: CountryService = Depends(get_country_service),
):
    """
    Lấy danh sách countries với phân trang
    """
    return await service.get_countries_paginated(page=page, page_size=page_size)


@router.get(
    "/{code}", response_model=CountryRead, summary="Lấy thông tin country theo code"
)
async def get_country(
    code: str, service: CountryService = Depends(get_country_service)
):
    """
    Lấy thông tin country theo code. Ném 404 nếu không tồn tại
    """
    country = await service.get_country_by_code(code)
    return CountryRead.model_validate(country, from_attributes=True)


@router.put("/{code}", response_model=CountryRead, summary="Cập nhật thông tin country")
async def update_country(
    code: str,
    country_in: CountryUpdate,
    service: CountryService = Depends(get_country_service),
):
    """
    Cập nhật country theo code
    """
    return await service.update_country(code, country_in)


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa country")
async def delete_country(
    code: str, service: CountryService = Depends(get_country_service)
):
    """
    Xóa country (hard delete). Có thể đổi thành soft delete nếu cần
    """
    await service.delete_country(code)
    return None


@router.get(
    "/search/mixin",
    response_model=dict,
    summary="Tìm kiếm countries theo code hoặc name",
)
async def search_countries(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: CountryService = Depends(get_country_service),
):
    """
    Search countries in both code and name columns

    Examples:
    - `/country/search/mixin?q=VN` → tìm "VN" trong code hoặc name (không phân biệt hoa/thường)
    - `/country/search/mixin?q=Vietnam&exact_match=true` → tìm chính xác name
    - `/country/search/mixin?q=US&case_sensitive=true` → chỉ tìm "US" (viết hoa)
    """
    return await service.search_countries(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )

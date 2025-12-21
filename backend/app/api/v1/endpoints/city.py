# app/api/v1/endpoints/city.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.city import CityCreate, CityRead, CityUpdate
from app.services.city import CityService

router = APIRouter()


def get_city_service(db: AsyncSession = Depends(get_async_session)) -> CityService:
    return CityService(db)


@router.post(
    "/",
    response_model=CityRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo city mới",
    description="Tạo city mới với country_code và name",
)
async def create_city(
    city_in: CityCreate, service: CityService = Depends(get_city_service)
):
    """
    Endpoint tạo city mới với validation unique constraint (country_code, name)
    """
    return await service.create_city(city_in)


@router.get("/{city_id}", response_model=CityRead, summary="Lấy thông tin city theo ID")
async def get_city(
    city_id: UUID, service: CityService = Depends(get_city_service)
):
    """
    Lấy thông tin city theo ID. Ném 404 nếu không tồn tại
    """
    city = await service.get_city_by_id(city_id)
    return CityRead.model_validate(city, from_attributes=True)


@router.get("/", response_model=dict, summary="Danh sách cities có phân trang")
async def get_cities(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    country_code: str | None = Query(None, min_length=2, max_length=2, description="Lọc theo mã quốc gia (ISO 3166-1 alpha-2), ví dụ: 'VN'"),
    service: CityService = Depends(get_city_service),
):
    """
    Truy xuất danh sách các thành phố (Cities) hỗ trợ phân trang và lọc theo quốc gia.

    Hàm này trả về thông tin định danh và tên của các thành phố. Hữu ích cho việc
    xây dựng các dropdown menu địa điểm hoặc validate dữ liệu địa lý.

    Args:
        page (int): Số thứ tự trang hiện tại (bắt đầu từ 1). Mặc định là 1.
        page_size (int): Số lượng bản ghi trên một trang (giới hạn 1-100). Mặc định là 20.
        country_code (str, optional): Mã quốc gia 2 ký tự để lọc thành phố.
                                      Ví dụ: "VN" cho Việt Nam, "US" cho Mỹ.

    Returns:
        dict: Một từ điển chứa danh sách thành phố và metadata phân trang.

    Response Schema:
        {
            "items": [
                {
                    "id": UUID,            # ID định danh duy nhất của thành phố (UUID)
                    "country_code": str,   # Mã quốc gia (VD: "VN")
                    "name": str            # Tên hiển thị của thành phố (VD: "Hà Nội")
                }
            ],
            "total": int,        # Tổng số bản ghi tìm thấy
            "page": int,         # Trang hiện tại
            "page_size": int,    # Kích thước trang
            "total_pages": int   # Tổng số trang tính toán được
        }

    Example Response:
        {
            "items": [
                {
                    "id": "d2063e38-ff44-46e3-bd90-e529b449e642",
                    "country_code": "VN",
                    "name": "Hà Nội"
                },
                {
                    "id": "15e3fa91-a5e9-42fb-8503-8df6f233cf12",
                    "country_code": "VN",
                    "name": "Thành phố Hồ Chí Minh"
                }
            ],
            "total": 15,
            "page": 1,
            "page_size": 20,
            "total_pages": 1
        }
    """
    return await service.get_cities_paginated(
        page=page, page_size=page_size, country_code=country_code
    )


@router.put("/{city_id}", response_model=CityRead, summary="Cập nhật thông tin city")
async def update_city(
    city_id: UUID, city_in: CityUpdate, service: CityService = Depends(get_city_service)
):
    """
    Cập nhật city theo ID
    """
    return await service.update_city(city_id, city_in)


@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa city")
async def delete_city(
    city_id: UUID, service: CityService = Depends(get_city_service)
):
    """
    Xóa city (hard delete). Có thể đổi thành soft delete nếu cần
    """
    await service.delete_city(city_id)
    return None


@router.get(
    "/search/mixin", response_model=dict, summary="Tìm kiếm cities theo name hoặc country_code"
)
async def search_cities(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: CityService = Depends(get_city_service),
):
    """
    Search cities in both name and country_code columns

    Examples:
    - `/city/search/mixin?q=Hanoi` → tìm "Hanoi" trong name hoặc country_code (không phân biệt hoa/thường)
    - `/city/search/mixin?q=VN&exact_match=true` → tìm chính xác country_code
    - `/city/search/mixin?q=Ho Chi Minh&case_sensitive=true` → chỉ tìm "Ho Chi Minh" (phân biệt hoa/thường)
    """
    return await service.search_cities(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )


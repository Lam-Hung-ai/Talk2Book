# app/api/v1/endpoints/airport.py
from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.airport import AirportCreate, AirportRead, AirportUpdate
from app.services.airport import AirportService

router = APIRouter()


def get_airport_service(db: AsyncSession = Depends(get_async_session)) -> AirportService:
    return AirportService(db)


@router.post(
    "/",
    response_model=AirportRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo airport mới",
    description="Tạo airport mới với city_id, name, timezone và optional iata/icao",
)
async def create_airport(
    airport_in: AirportCreate, service: AirportService = Depends(get_airport_service)
):
    """
    Endpoint tạo airport mới với validation unique constraint (city_id, name) và unique iata/icao
    """
    return await service.create_airport(airport_in)


@router.get("/{iata}", response_model=AirportRead, summary="Lấy thông tin airport theo IATA code")
async def get_airport(
    iata: str, service: AirportService = Depends(get_airport_service)
):
    """
    Lấy thông tin airport theo IATA code. Ném 404 nếu không tồn tại
    """
    airport = await service.get_airport_by_iata(iata)
    return AirportRead.model_validate(airport, from_attributes=True)


@router.get("/", response_model=dict, summary="Danh sách airports có phân trang")
async def get_airports(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    city_id: str | None = Query(None, description="Lọc theo city ID"),
    service: AirportService = Depends(get_airport_service),
):
    """
    Lấy danh sách airports với phân trang và filter theo city_id
    """
    from uuid import UUID
    city_uuid = UUID(city_id) if city_id else None
    return await service.get_airports_paginated(
        page=page, page_size=page_size, city_id=city_uuid
    )


@router.put("/{iata}", response_model=AirportRead, summary="Cập nhật thông tin airport")
async def update_airport(
    iata: str, airport_in: AirportUpdate, service: AirportService = Depends(get_airport_service)
):
    """
    Cập nhật airport theo IATA code
    """
    return await service.update_airport(iata, airport_in)


@router.delete("/{iata}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa airport")
async def delete_airport(
    iata: str, service: AirportService = Depends(get_airport_service)
):
    """
    Xóa airport (hard delete). Có thể đổi thành soft delete nếu cần
    """
    await service.delete_airport(iata)
    return None


@router.get(
    "/search/mixin", response_model=dict, summary="Tìm kiếm airports theo name, iata hoặc icao"
)
async def search_airports(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: AirportService = Depends(get_airport_service),
):
    """
    Search airports in name, iata, and icao columns

    Examples:
    - `/airport/search/mixin?q=SGN` → tìm "SGN" trong name, iata hoặc icao (không phân biệt hoa/thường)
    - `/airport/search/mixin?q=SGN&exact_match=true` → tìm chính xác IATA code
    - `/airport/search/mixin?q=Tan Son Nhat&case_sensitive=true` → chỉ tìm "Tan Son Nhat" (phân biệt hoa/thường)
    """
    return await service.search_airports(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )


# app/api/v1/endpoints/hotel.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.hotel import HotelCreate, HotelRead, HotelUpdate
from app.services.hotel import HotelService

router = APIRouter()


def get_hotel_service(db: AsyncSession = Depends(get_async_session)) -> HotelService:
    return HotelService(db)


@router.post(
    "/",
    response_model=HotelRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo hotel mới",
)
async def create_hotel(
    hotel_in: HotelCreate, service: HotelService = Depends(get_hotel_service)
):
    """Endpoint tạo hotel mới"""
    return await service.create_hotel(hotel_in)


@router.get("/{hotel_id}", response_model=HotelRead, summary="Lấy thông tin hotel theo ID")
async def get_hotel(
    hotel_id: UUID, service: HotelService = Depends(get_hotel_service)
):
    """Lấy thông tin hotel theo ID. Ném 404 nếu không tồn tại"""
    hotel = await service.get_hotel_by_id(hotel_id)
    return HotelRead.model_validate(hotel, from_attributes=True)


@router.get("/", response_model=dict, summary="Danh sách hotels có phân trang")
async def get_hotels(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    city_id: UUID | None = Query(None, description="Lọc theo city_id"),
    provider_id: UUID | None = Query(None, description="Lọc theo provider_id"),
    service: HotelService = Depends(get_hotel_service),
):
    """Lấy danh sách hotels với phân trang và filter"""
    return await service.get_hotels_paginated(
        page=page, page_size=page_size, city_id=city_id, provider_id=provider_id
    )


@router.put("/{hotel_id}", response_model=HotelRead, summary="Cập nhật thông tin hotel")
async def update_hotel(
    hotel_id: UUID,
    hotel_in: HotelUpdate,
    service: HotelService = Depends(get_hotel_service),
):
    """Cập nhật hotel"""
    return await service.update_hotel(hotel_id, hotel_in)


@router.delete(
    "/{hotel_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa hotel"
)
async def delete_hotel(
    hotel_id: UUID, service: HotelService = Depends(get_hotel_service)
):
    """Xóa hotel"""
    await service.delete_hotel(hotel_id)
    return None


@router.get(
    "/search/mixin", response_model=dict, summary="Tìm kiếm hotels theo name hoặc address"
)
async def search_mixin_hotels(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: HotelService = Depends(get_hotel_service),
):
    """Search hotels theo name và address"""
    return await service.search_hotels(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )


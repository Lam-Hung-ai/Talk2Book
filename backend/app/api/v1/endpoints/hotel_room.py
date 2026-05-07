# app/api/v1/endpoints/hotel_room.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.hotel_room import HotelRoomCreate, HotelRoomRead, HotelRoomUpdate
from app.services.hotel_room import HotelRoomService

router = APIRouter()


def get_hotel_room_service(
    db: AsyncSession = Depends(get_async_session),
) -> HotelRoomService:
    return HotelRoomService(db)


@router.post(
    "/",
    response_model=HotelRoomRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo hotel room mới",
)
async def create_hotel_room(
    room_in: HotelRoomCreate,
    service: HotelRoomService = Depends(get_hotel_room_service),
):
    """Endpoint tạo hotel room mới"""
    return await service.create_hotel_room(room_in)


@router.get(
    "/{room_id}",
    response_model=HotelRoomRead,
    summary="Lấy thông tin hotel room theo ID",
)
async def get_hotel_room(
    room_id: UUID, service: HotelRoomService = Depends(get_hotel_room_service)
):
    """Lấy thông tin hotel room theo ID. Ném 404 nếu không tồn tại"""
    room = await service.get_hotel_room_by_id(room_id)
    return HotelRoomRead.model_validate(room, from_attributes=True)


@router.get("/", response_model=dict, summary="Danh sách hotel rooms có phân trang")
async def get_hotel_rooms(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    hotel_id: UUID | None = Query(None, description="Lọc theo hotel_id"),
    service: HotelRoomService = Depends(get_hotel_room_service),
):
    """Lấy danh sách hotel rooms với phân trang và filter"""
    return await service.get_hotel_rooms_paginated(
        page=page, page_size=page_size, hotel_id=hotel_id
    )


@router.put(
    "/{room_id}", response_model=HotelRoomRead, summary="Cập nhật thông tin hotel room"
)
async def update_hotel_room(
    room_id: UUID,
    room_in: HotelRoomUpdate,
    service: HotelRoomService = Depends(get_hotel_room_service),
):
    """Cập nhật hotel room"""
    return await service.update_hotel_room(room_id, room_in)


@router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa hotel room",
)
async def delete_hotel_room(
    room_id: UUID, service: HotelRoomService = Depends(get_hotel_room_service)
):
    """Xóa hotel room"""
    await service.delete_hotel_room(room_id)
    return None


@router.get(
    "/search/mixin",
    response_model=dict,
    summary="Tìm kiếm hotel rooms theo code hoặc bed_config",
)
async def search_hotel_rooms(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    exact_match: bool = Query(False, description="Tìm chính xác toàn bộ chuỗi"),
    case_sensitive: bool = Query(False, description="Phân biệt hoa/thường"),
    service: HotelRoomService = Depends(get_hotel_room_service),
):
    """Search hotel rooms theo code và bed_config"""
    return await service.search_hotel_rooms(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )

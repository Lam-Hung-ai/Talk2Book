from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.booking import BookingCreate, BookingRead, BookingUpdate
from app.schemas.booking_flow import (
    FlightBookingRequest,
    FlightBookingResult,
    HotelBookingRequest,
    HotelBookingResult,
)
from app.services.booking import BookingService

router = APIRouter()


def get_booking_service(db: AsyncSession = Depends(get_async_session)) -> BookingService:
    return BookingService(db)


@router.post(
    "/",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo booking",
)
async def create_booking(
    booking_in: BookingCreate, service: BookingService = Depends(get_booking_service)
):
    return await service.create_booking(booking_in)


@router.get(
    "/{booking_id}",
    response_model=BookingRead,
    summary="Lấy booking theo ID",
)
async def get_booking(booking_id: UUID, service: BookingService = Depends(get_booking_service)):
    return await service.get_booking(booking_id)


@router.get("/", response_model=dict, summary="Danh sách booking có phân trang")
async def list_bookings(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user_id: UUID | None = Query(None),
    state: str | None = Query(None),
    service: BookingService = Depends(get_booking_service),
):
    return await service.list_bookings(
        page=page,
        page_size=page_size,
        user_id=user_id,
        state=state,
    )


@router.put(
    "/{booking_id}",
    response_model=BookingRead,
    summary="Cập nhật booking",
)
async def update_booking(
    booking_id: UUID,
    booking_in: BookingUpdate,
    service: BookingService = Depends(get_booking_service),
):
    return await service.update_booking(booking_id, booking_in)


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa booking",
)
async def delete_booking(booking_id: UUID, service: BookingService = Depends(get_booking_service)):
    await service.delete_booking(booking_id)
    return None


@router.get("/search/mixin", response_model=dict, summary="Tìm kiếm booking")
async def search_bookings(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    exact_match: bool = Query(False),
    case_sensitive: bool = Query(False),
    service: BookingService = Depends(get_booking_service),
):
    return await service.search_bookings(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )


# ---------- FLOW: ĐẶT VÉ MÁY BAY & ĐẶT PHÒNG ----------


@router.post(
    "/flight-booking",
    response_model=FlightBookingResult,
    status_code=status.HTTP_201_CREATED,
    summary="Đặt vé máy bay từ kết quả search",
)
async def create_flight_booking(
    payload: FlightBookingRequest,
    service: BookingService = Depends(get_booking_service),
):
    """
    Tạo booking vé máy bay dựa trên `FlightInstance` + `SeatInventory`.
    Dùng sau khi user đã search chuyến bay và chọn 1 option cụ thể.
    """

    return await service.create_flight_booking(payload)


@router.post(
    "/hotel-booking",
    response_model=HotelBookingResult,
    status_code=status.HTTP_201_CREATED,
    summary="Đặt phòng khách sạn từ kết quả search",
)
async def create_hotel_booking(
    payload: HotelBookingRequest,
    service: BookingService = Depends(get_booking_service),
):
    """
    Tạo booking khách sạn dựa trên `HotelRoom` + `RoomRatePlan` + `RoomInventoryDaily`.
    Dùng sau khi user đã search khách sạn và chọn 1 loại phòng + gói giá.
    """

    return await service.create_hotel_booking(payload)



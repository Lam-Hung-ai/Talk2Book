from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.booking import BookingCreate, BookingRead, BookingUpdate
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


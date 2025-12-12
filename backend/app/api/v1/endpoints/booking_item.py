from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.booking_item import BookingItemCreate, BookingItemRead, BookingItemUpdate
from app.services.booking_item import BookingItemService

router = APIRouter()


def get_booking_item_service(
    db: AsyncSession = Depends(get_async_session),
) -> BookingItemService:
    return BookingItemService(db)


@router.post(
    "/",
    response_model=BookingItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo booking item",
)
async def create_booking_item(
    item_in: BookingItemCreate,
    service: BookingItemService = Depends(get_booking_item_service),
):
    return await service.create_item(item_in)


@router.get(
    "/{item_id}",
    response_model=BookingItemRead,
    summary="Lấy booking item theo ID",
)
async def get_booking_item(
    item_id: UUID, service: BookingItemService = Depends(get_booking_item_service)
):
    return await service.get_item(item_id)


@router.get("/", response_model=dict, summary="Danh sách booking item")
async def list_booking_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    booking_id: UUID | None = Query(None),
    service: BookingItemService = Depends(get_booking_item_service),
):
    return await service.list_items(
        page=page,
        page_size=page_size,
        booking_id=booking_id,
    )


@router.put(
    "/{item_id}",
    response_model=BookingItemRead,
    summary="Cập nhật booking item",
)
async def update_booking_item(
    item_id: UUID,
    item_in: BookingItemUpdate,
    service: BookingItemService = Depends(get_booking_item_service),
):
    return await service.update_item(item_id, item_in)


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa booking item",
)
async def delete_booking_item(
    item_id: UUID,
    service: BookingItemService = Depends(get_booking_item_service),
):
    await service.delete_item(item_id)
    return None


@router.get("/search/mixin", response_model=dict, summary="Tìm kiếm booking item")
async def search_booking_items(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    exact_match: bool = Query(False),
    case_sensitive: bool = Query(False),
    service: BookingItemService = Depends(get_booking_item_service),
):
    return await service.search_items(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )


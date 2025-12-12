from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.passenger import PassengerCreate, PassengerRead, PassengerUpdate
from app.services.passenger import PassengerService

router = APIRouter()


def get_passenger_service(db: AsyncSession = Depends(get_async_session)) -> PassengerService:
    return PassengerService(db)


@router.post(
    "/",
    response_model=PassengerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo passenger",
)
async def create_passenger(
    passenger_in: PassengerCreate, service: PassengerService = Depends(get_passenger_service)
):
    return await service.create_passenger(passenger_in)


@router.get(
    "/{passenger_id}",
    response_model=PassengerRead,
    summary="Lấy passenger theo ID",
)
async def get_passenger(
    passenger_id: UUID, service: PassengerService = Depends(get_passenger_service)
):
    return await service.get_passenger(passenger_id)


@router.get("/", response_model=dict, summary="Danh sách passenger")
async def list_passengers(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    booking_id: UUID | None = Query(None),
    service: PassengerService = Depends(get_passenger_service),
):
    return await service.list_passengers(
        page=page,
        page_size=page_size,
        booking_id=booking_id,
    )


@router.put(
    "/{passenger_id}",
    response_model=PassengerRead,
    summary="Cập nhật passenger",
)
async def update_passenger(
    passenger_id: UUID,
    passenger_in: PassengerUpdate,
    service: PassengerService = Depends(get_passenger_service),
):
    return await service.update_passenger(passenger_id, passenger_in)


@router.delete(
    "/{passenger_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa passenger",
)
async def delete_passenger(
    passenger_id: UUID, service: PassengerService = Depends(get_passenger_service)
):
    await service.delete_passenger(passenger_id)
    return None


@router.get("/search/mixin", response_model=dict, summary="Tìm kiếm passenger")
async def search_passengers(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    exact_match: bool = Query(False),
    case_sensitive: bool = Query(False),
    service: PassengerService = Depends(get_passenger_service),
):
    return await service.search_passengers(
        q=q,
        page=page,
        page_size=page_size,
        exact_match=exact_match,
        case_sensitive=case_sensitive,
    )


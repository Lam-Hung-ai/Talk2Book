from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.models.enums import CabinType
from app.schemas.seat_inventory import (
    SeatInventoryCreate,
    SeatInventoryRead,
    SeatInventoryUpdate,
)
from app.services.seat_inventory import SeatInventoryService

router = APIRouter()


def get_seat_inventory_service(
    db: AsyncSession = Depends(get_async_session),
) -> SeatInventoryService:
    return SeatInventoryService(db)


@router.post(
    "/",
    response_model=SeatInventoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo seat inventory",
)
async def create_seat_inventory(
    payload: SeatInventoryCreate,
    service: SeatInventoryService = Depends(get_seat_inventory_service),
):
    return await service.create_inventory(payload)


@router.get("/", response_model=dict, summary="Danh sách seat inventory")
async def list_seat_inventory(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    instance_id: UUID | None = Query(None),
    service: SeatInventoryService = Depends(get_seat_inventory_service),
):
    return await service.list_inventory(
        page=page, page_size=page_size, instance_id=instance_id
    )


@router.get(
    "/{instance_id}/{cabin}",
    response_model=SeatInventoryRead,
    summary="Chi tiết seat inventory",
)
async def get_seat_inventory(
    instance_id: UUID,
    cabin: CabinType = Path(...),
    service: SeatInventoryService = Depends(get_seat_inventory_service),
):
    return await service.get_inventory(instance_id, cabin)


@router.put(
    "/{instance_id}/{cabin}",
    response_model=SeatInventoryRead,
    summary="Cập nhật seat inventory",
)
async def update_seat_inventory(
    instance_id: UUID,
    cabin: CabinType = Path(...),
    payload: SeatInventoryUpdate = Body(...),
    service: SeatInventoryService = Depends(get_seat_inventory_service),
):
    return await service.update_inventory(instance_id, cabin, payload)


@router.delete(
    "/{instance_id}/{cabin}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa seat inventory",
)
async def delete_seat_inventory(
    instance_id: UUID,
    cabin: CabinType = Path(...),
    service: SeatInventoryService = Depends(get_seat_inventory_service),
):
    await service.delete_inventory(instance_id, cabin)
    return None

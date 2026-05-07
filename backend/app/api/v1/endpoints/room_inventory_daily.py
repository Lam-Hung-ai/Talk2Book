# app/api/v1/endpoints/room_inventory_daily.py
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.room_inventory_daily import (
    RoomInventoryDailyCreate,
    RoomInventoryDailyRead,
    RoomInventoryDailyUpdate,
)
from app.services.room_inventory_daily import RoomInventoryDailyService

router = APIRouter()


def get_room_inventory_daily_service(
    db: AsyncSession = Depends(get_async_session),
) -> RoomInventoryDailyService:
    return RoomInventoryDailyService(db)


@router.post(
    "/",
    response_model=RoomInventoryDailyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo room inventory daily mới",
)
async def create_room_inventory_daily(
    inventory_in: RoomInventoryDailyCreate,
    service: RoomInventoryDailyService = Depends(get_room_inventory_daily_service),
):
    """Endpoint tạo room inventory daily mới"""
    return await service.create_room_inventory_daily(inventory_in)


@router.get(
    "/{room_id}/{rate_plan_id}/{stay_date}",
    response_model=RoomInventoryDailyRead,
    summary="Lấy thông tin room inventory daily theo composite key",
)
async def get_room_inventory_daily(
    room_id: UUID,
    rate_plan_id: UUID,
    stay_date: date,
    service: RoomInventoryDailyService = Depends(get_room_inventory_daily_service),
):
    """Lấy thông tin room inventory daily theo composite key (room_id, rate_plan_id, stay_date). Ném 404 nếu không tồn tại"""
    inventory = await service.get_room_inventory_daily(room_id, rate_plan_id, stay_date)
    return RoomInventoryDailyRead.model_validate(inventory, from_attributes=True)


@router.get(
    "/", response_model=dict, summary="Danh sách room inventory dailies có phân trang"
)
async def get_room_inventory_dailies(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    room_id: UUID | None = Query(None, description="Lọc theo room_id"),
    rate_plan_id: UUID | None = Query(None, description="Lọc theo rate_plan_id"),
    stay_date_from: date | None = Query(None, description="Lọc từ ngày"),
    stay_date_to: date | None = Query(None, description="Lọc đến ngày"),
    service: RoomInventoryDailyService = Depends(get_room_inventory_daily_service),
):
    """Lấy danh sách room inventory dailies với phân trang và filter"""
    return await service.get_room_inventory_dailies_paginated(
        page=page,
        page_size=page_size,
        room_id=room_id,
        rate_plan_id=rate_plan_id,
        stay_date_from=stay_date_from,
        stay_date_to=stay_date_to,
    )


@router.put(
    "/{room_id}/{rate_plan_id}/{stay_date}",
    response_model=RoomInventoryDailyRead,
    summary="Cập nhật thông tin room inventory daily",
)
async def update_room_inventory_daily(
    room_id: UUID,
    rate_plan_id: UUID,
    stay_date: date,
    inventory_in: RoomInventoryDailyUpdate,
    service: RoomInventoryDailyService = Depends(get_room_inventory_daily_service),
):
    """Cập nhật room inventory daily"""
    return await service.update_room_inventory_daily(
        room_id, rate_plan_id, stay_date, inventory_in
    )


@router.delete(
    "/{room_id}/{rate_plan_id}/{stay_date}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa room inventory daily",
)
async def delete_room_inventory_daily(
    room_id: UUID,
    rate_plan_id: UUID,
    stay_date: date,
    service: RoomInventoryDailyService = Depends(get_room_inventory_daily_service),
):
    """Xóa room inventory daily"""
    await service.delete_room_inventory_daily(room_id, rate_plan_id, stay_date)
    return None

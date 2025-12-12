# app/api/v1/endpoints/time_slot.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.time_slot import TimeSlotCreate, TimeSlotRead, TimeSlotUpdate
from app.services.time_slot import TimeSlotService

router = APIRouter()


def get_time_slot_service(db: AsyncSession = Depends(get_async_session)) -> TimeSlotService:
    return TimeSlotService(db)


@router.post(
    "/",
    response_model=TimeSlotRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo time_slot mới",
)
async def create_time_slot(
    time_slot_in: TimeSlotCreate, service: TimeSlotService = Depends(get_time_slot_service)
):
    """Tạo time_slot mới"""
    return await service.create_time_slot(time_slot_in)


@router.get("/{time_slot_id}", response_model=TimeSlotRead, summary="Lấy thông tin time_slot theo ID")
async def get_time_slot(time_slot_id: UUID, service: TimeSlotService = Depends(get_time_slot_service)):
    """Lấy thông tin time_slot theo ID. Ném 404 nếu không tồn tại"""
    time_slot = await service.get_time_slot_by_id(time_slot_id)
    return TimeSlotRead.model_validate(time_slot, from_attributes=True)


@router.get("/", response_model=dict, summary="Danh sách time_slots có phân trang")
async def get_time_slots(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    product_id: UUID | None = Query(None, description="Lọc theo product_id"),
    service: TimeSlotService = Depends(get_time_slot_service),
):
    """Lấy danh sách time_slots với phân trang và filter"""
    return await service.get_time_slots_paginated(
        page=page, page_size=page_size, product_id=product_id
    )


@router.put("/{time_slot_id}", response_model=TimeSlotRead, summary="Cập nhật thông tin time_slot")
async def update_time_slot(
    time_slot_id: UUID, time_slot_in: TimeSlotUpdate, service: TimeSlotService = Depends(get_time_slot_service)
):
    """Cập nhật time_slot"""
    return await service.update_time_slot(time_slot_id, time_slot_in)


@router.delete("/{time_slot_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa time_slot")
async def delete_time_slot(time_slot_id: UUID, service: TimeSlotService = Depends(get_time_slot_service)):
    """Xóa time_slot"""
    await service.delete_time_slot(time_slot_id)
    return None


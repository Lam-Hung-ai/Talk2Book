# app/api/v1/endpoints/time_slot.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.time_slot import TimeSlotCreate, TimeSlotRead, TimeSlotUpdate
from app.services.time_slot import TimeSlotService

router = APIRouter()


def get_time_slot_service(
    db: AsyncSession = Depends(get_async_session),
) -> TimeSlotService:
    return TimeSlotService(db)


@router.post(
    "/",
    response_model=TimeSlotRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo time slot mới",
)
async def create_time_slot(
    payload: TimeSlotCreate, service: TimeSlotService = Depends(get_time_slot_service)
):
    return await service.create_time_slot(payload)


@router.get("/", response_model=dict, summary="Danh sách time slots có phân trang")
async def list_time_slots(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    q: str | None = Query(None, description="Tìm kiếm theo product_id"),
    product_id: UUID | None = Query(None, description="Lọc theo product"),
    service: TimeSlotService = Depends(get_time_slot_service),
):
    return await service.list_time_slots(
        page=page, page_size=page_size, q=q, product_id=product_id
    )


@router.get("/{time_slot_id}", response_model=TimeSlotRead, summary="Chi tiết time slot")
async def get_time_slot(
    time_slot_id: UUID, service: TimeSlotService = Depends(get_time_slot_service)
):
    return await service.get_time_slot(time_slot_id)


@router.put("/{time_slot_id}", response_model=TimeSlotRead, summary="Cập nhật time slot")
async def update_time_slot(
    time_slot_id: UUID,
    payload: TimeSlotUpdate,
    service: TimeSlotService = Depends(get_time_slot_service),
):
    return await service.update_time_slot(time_slot_id, payload)


@router.delete(
    "/{time_slot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa time slot",
)
async def delete_time_slot(
    time_slot_id: UUID, service: TimeSlotService = Depends(get_time_slot_service)
):
    await service.delete_time_slot(time_slot_id)
    return None


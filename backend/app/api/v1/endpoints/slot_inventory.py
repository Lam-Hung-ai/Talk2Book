# app/api/v1/endpoints/slot_inventory.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.slot_inventory import (
    SlotInventoryCreate,
    SlotInventoryRead,
    SlotInventoryUpdate,
)
from app.services.slot_inventory import SlotInventoryService

router = APIRouter()


def get_slot_inventory_service(
    db: AsyncSession = Depends(get_async_session),
) -> SlotInventoryService:
    return SlotInventoryService(db)


@router.post(
    "/",
    response_model=SlotInventoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo slot inventory mới",
)
async def create_slot_inventory(
    payload: SlotInventoryCreate,
    service: SlotInventoryService = Depends(get_slot_inventory_service),
):
    return await service.create_slot_inventory(payload)


@router.get(
    "/", response_model=dict, summary="Danh sách slot inventories có phân trang"
)
async def list_slot_inventories(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    q: str | None = Query(None, description="Tìm kiếm theo slot_id hoặc currency_code"),
    slot_id: UUID | None = Query(None, description="Lọc theo slot"),
    service: SlotInventoryService = Depends(get_slot_inventory_service),
):
    return await service.list_slot_inventories(
        page=page, page_size=page_size, q=q, slot_id=slot_id
    )


@router.get(
    "/{slot_id}", response_model=SlotInventoryRead, summary="Chi tiết slot inventory"
)
async def get_slot_inventory(
    slot_id: UUID, service: SlotInventoryService = Depends(get_slot_inventory_service)
):
    return await service.get_slot_inventory(slot_id)


@router.put(
    "/{slot_id}", response_model=SlotInventoryRead, summary="Cập nhật slot inventory"
)
async def update_slot_inventory(
    slot_id: UUID,
    payload: SlotInventoryUpdate,
    service: SlotInventoryService = Depends(get_slot_inventory_service),
):
    return await service.update_slot_inventory(slot_id, payload)


@router.delete(
    "/{slot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa slot inventory",
)
async def delete_slot_inventory(
    slot_id: UUID, service: SlotInventoryService = Depends(get_slot_inventory_service)
):
    await service.delete_slot_inventory(slot_id)
    return None


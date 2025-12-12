# app/api/v1/endpoints/slot_inventory.py
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.deps import get_async_session
from app.schemas.slot_inventory import SlotInventoryCreate, SlotInventoryRead, SlotInventoryUpdate
from app.services.slot_inventory import SlotInventoryService

router = APIRouter()


def get_slot_inventory_service(db: AsyncSession = Depends(get_async_session)) -> SlotInventoryService:
    return SlotInventoryService(db)


@router.post(
    "/",
    response_model=SlotInventoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo slot_inventory mới",
)
async def create_slot_inventory(
    slot_inventory_in: SlotInventoryCreate, service: SlotInventoryService = Depends(get_slot_inventory_service)
):
    """Tạo slot_inventory mới"""
    return await service.create_slot_inventory(slot_inventory_in)


@router.get("/{slot_id}", response_model=SlotInventoryRead, summary="Lấy thông tin slot_inventory theo slot_id")
async def get_slot_inventory(slot_id: UUID, service: SlotInventoryService = Depends(get_slot_inventory_service)):
    """Lấy thông tin slot_inventory theo slot_id. Ném 404 nếu không tồn tại"""
    slot_inventory = await service.get_slot_inventory_by_id(slot_id)
    return SlotInventoryRead.model_validate(slot_inventory, from_attributes=True)


@router.get("/", response_model=dict, summary="Danh sách slot_inventories có phân trang")
async def get_slot_inventories(
    page: int = Query(1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng mỗi trang"),
    service: SlotInventoryService = Depends(get_slot_inventory_service),
):
    """Lấy danh sách slot_inventories với phân trang"""
    return await service.get_slot_inventories_paginated(
        page=page, page_size=page_size
    )


@router.put("/{slot_id}", response_model=SlotInventoryRead, summary="Cập nhật thông tin slot_inventory")
async def update_slot_inventory(
    slot_id: UUID, slot_inventory_in: SlotInventoryUpdate, service: SlotInventoryService = Depends(get_slot_inventory_service)
):
    """Cập nhật slot_inventory"""
    return await service.update_slot_inventory(slot_id, slot_inventory_in)


@router.delete("/{slot_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa slot_inventory")
async def delete_slot_inventory(slot_id: UUID, service: SlotInventoryService = Depends(get_slot_inventory_service)):
    """Xóa slot_inventory"""
    await service.delete_slot_inventory(slot_id)
    return None


# app/services/slot_inventory.py
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.slot_inventory import SlotInventory
from app.repositories.slot_inventory import SlotInventoryRepository
from app.schemas.slot_inventory import (
    SlotInventoryCreate,
    SlotInventoryRead,
    SlotInventoryUpdate,
)


class SlotInventoryService:
    def __init__(self, db: AsyncSession):
        self.repo = SlotInventoryRepository(db)
        self.db = db

    async def get_slot_inventory_by_id(self, slot_id: UUID) -> SlotInventory:
        """Lấy slot_inventory theo slot_id, ném 404 nếu không tồn tại"""
        return await self.repo.get_or_404(slot_id, detail="Slot inventory không tồn tại")

    async def create_slot_inventory(self, slot_inventory_in: SlotInventoryCreate) -> SlotInventoryRead:
        """Tạo slot_inventory mới"""
        # Validate sold <= capacity
        if slot_inventory_in.sold > slot_inventory_in.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sold không được lớn hơn capacity"
            )

        db_slot_inventory = await self.repo.create(slot_inventory_in)
        return SlotInventoryRead.model_validate(db_slot_inventory, from_attributes=True)

    async def get_slot_inventories_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Lấy danh sách slot_inventories có phân trang"""
        skip = (page - 1) * page_size

        slot_inventories = await self.repo.get_multi(skip=skip, limit=page_size)
        total = await self.repo.get_count()

        return {
            "items": [SlotInventoryRead.model_validate(si, from_attributes=True) for si in slot_inventories],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def update_slot_inventory(self, slot_id: UUID, slot_inventory_in: SlotInventoryUpdate) -> SlotInventoryRead:
        """Cập nhật slot_inventory"""
        db_slot_inventory = await self.get_slot_inventory_by_id(slot_id)

        # Validate sold <= capacity nếu có update
        capacity = slot_inventory_in.capacity if slot_inventory_in.capacity is not None else db_slot_inventory.capacity
        sold = slot_inventory_in.sold if slot_inventory_in.sold is not None else db_slot_inventory.sold

        if sold > capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sold không được lớn hơn capacity"
            )

        updated_slot_inventory = await self.repo.update(db_slot_inventory, slot_inventory_in)
        return SlotInventoryRead.model_validate(updated_slot_inventory, from_attributes=True)

    async def delete_slot_inventory(self, slot_id: UUID) -> None:
        """Xóa slot_inventory"""
        await self.repo.delete(slot_id)


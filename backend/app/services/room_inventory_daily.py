# app/services/room_inventory_daily.py
from datetime import date
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.room_inventory_daily import RoomInventoryDaily
from app.repositories.room_inventory_daily import RoomInventoryDailyRepository
from app.schemas.room_inventory_daily import (
    RoomInventoryDailyCreate,
    RoomInventoryDailyRead,
    RoomInventoryDailyUpdate,
)


class RoomInventoryDailyService:
    def __init__(self, db: AsyncSession):
        self.repo = RoomInventoryDailyRepository(db)
        self.db = db

    async def get_room_inventory_daily(
        self, room_id: UUID, rate_plan_id: UUID, stay_date: date
    ) -> RoomInventoryDaily:
        """Lấy inventory theo composite key, ném 404 nếu không tồn tại"""
        inventory = await self.repo.get_by_room_rate_date(
            str(room_id), str(rate_plan_id), stay_date
        )
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room inventory không tồn tại",
            )
        return inventory

    async def create_room_inventory_daily(
        self, inventory_in: RoomInventoryDailyCreate
    ) -> RoomInventoryDailyRead:
        """Tạo room inventory daily mới"""
        # Kiểm tra unique constraint: room_id + rate_plan_id + stay_date
        existing = await self.repo.get_by_room_rate_date(
            str(inventory_in.room_id),
            str(inventory_in.rate_plan_id),
            inventory_in.stay_date,
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Inventory đã tồn tại cho room, rate plan và ngày này",
            )

        # Kiểm tra constraint: sold <= allotment
        if inventory_in.sold > inventory_in.allotment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Số lượng đã bán không thể lớn hơn tổng số phòng",
            )

        db_inventory = await self.repo.create(inventory_in)
        return RoomInventoryDailyRead.model_validate(db_inventory, from_attributes=True)

    async def get_room_inventory_dailies_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        room_id: UUID | None = None,
        rate_plan_id: UUID | None = None,
        stay_date_from: date | None = None,
        stay_date_to: date | None = None,
    ) -> dict[str, Any]:
        """Lấy danh sách room inventory dailies có phân trang và filter"""
        skip = (page - 1) * page_size

        if stay_date_from and stay_date_to:
            inventories = await self.repo.get_by_date_range(
                stay_date_from, stay_date_to, skip=skip, limit=page_size
            )
            # Note: count_search không hỗ trợ date range, cần implement riêng hoặc dùng get_count với filter
            total = len(inventories)  # Tạm thời, có thể cải thiện sau
        else:
            filters = {}
            if room_id is not None:
                filters["room_id"] = room_id
            if rate_plan_id is not None:
                filters["rate_plan_id"] = rate_plan_id

            inventories = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
            total = await self.repo.get_count(**filters)

        return {
            "items": [
                RoomInventoryDailyRead.model_validate(inv, from_attributes=True)
                for inv in inventories
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_room_inventory_daily(
        self,
        room_id: UUID,
        rate_plan_id: UUID,
        stay_date: date,
        inventory_in: RoomInventoryDailyUpdate,
    ) -> RoomInventoryDailyRead:
        """Cập nhật room inventory daily"""
        db_inventory = await self.get_room_inventory_daily(room_id, rate_plan_id, stay_date)

        # Kiểm tra constraint: sold <= allotment
        allotment = inventory_in.allotment if inventory_in.allotment else db_inventory.allotment
        sold = inventory_in.sold if inventory_in.sold is not None else db_inventory.sold
        if sold > allotment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Số lượng đã bán không thể lớn hơn tổng số phòng",
            )

        updated_inventory = await self.repo.update(db_inventory, inventory_in)
        return RoomInventoryDailyRead.model_validate(
            updated_inventory, from_attributes=True
        )

    async def delete_room_inventory_daily(
        self, room_id: UUID, rate_plan_id: UUID, stay_date: date
    ) -> None:
        """Xóa room inventory daily"""
        db_inventory = await self.get_room_inventory_daily(room_id, rate_plan_id, stay_date)
        # Vì là composite key, cần xóa bằng cách set primary key
        await self.db.delete(db_inventory)
        await self.db.commit()

    async def search_room_inventory_dailies(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        """Tìm kiếm room inventory dailies (không có nhiều text fields để search)"""
        # RoomInventoryDaily không có nhiều text fields, có thể search theo stay_date nếu q là date
        # Tạm thời trả về empty hoặc implement logic riêng
        skip = (page - 1) * page_size

        # Vì không có text fields phù hợp, trả về empty result
        return {
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
        }


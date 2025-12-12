# app/services/time_slot.py
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.time_slot import TimeSlot
from app.repositories.time_slot import TimeSlotRepository
from app.schemas.time_slot import TimeSlotCreate, TimeSlotRead, TimeSlotUpdate


class TimeSlotService:
    def __init__(self, db: AsyncSession):
        self.repo = TimeSlotRepository(db)
        self.db = db

    async def get_time_slot_by_id(self, time_slot_id: UUID) -> TimeSlot:
        """Lấy time_slot theo ID, ném 404 nếu không tồn tại"""
        return await self.repo.get_or_404(time_slot_id, detail="Time slot không tồn tại")

    async def create_time_slot(self, time_slot_in: TimeSlotCreate) -> TimeSlotRead:
        """Tạo time_slot mới"""
        # Validate start_datetime < end_datetime
        if time_slot_in.start_datetime >= time_slot_in.end_datetime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_datetime phải nhỏ hơn end_datetime"
            )

        db_time_slot = await self.repo.create(time_slot_in)
        return TimeSlotRead.model_validate(db_time_slot, from_attributes=True)

    async def get_time_slots_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        product_id: UUID | None = None,
    ) -> dict[str, Any]:
        """Lấy danh sách time_slots có phân trang và filter"""
        skip = (page - 1) * page_size

        filters = {}
        if product_id is not None:
            filters["product_id"] = product_id

        time_slots = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [TimeSlotRead.model_validate(ts, from_attributes=True) for ts in time_slots],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def update_time_slot(self, time_slot_id: UUID, time_slot_in: TimeSlotUpdate) -> TimeSlotRead:
        """Cập nhật time_slot"""
        db_time_slot = await self.get_time_slot_by_id(time_slot_id)

        # Validate start_datetime < end_datetime nếu có update
        if time_slot_in.start_datetime is not None and time_slot_in.end_datetime is not None:
            if time_slot_in.start_datetime >= time_slot_in.end_datetime:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="start_datetime phải nhỏ hơn end_datetime"
                )
        elif time_slot_in.start_datetime is not None:
            if time_slot_in.start_datetime >= db_time_slot.end_datetime:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="start_datetime phải nhỏ hơn end_datetime"
                )
        elif time_slot_in.end_datetime is not None:
            if db_time_slot.start_datetime >= time_slot_in.end_datetime:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="start_datetime phải nhỏ hơn end_datetime"
                )

        updated_time_slot = await self.repo.update(db_time_slot, time_slot_in)
        return TimeSlotRead.model_validate(updated_time_slot, from_attributes=True)

    async def delete_time_slot(self, time_slot_id: UUID) -> None:
        """Xóa time_slot"""
        await self.repo.delete(time_slot_id)


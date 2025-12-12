# app/services/room_rate_plan.py
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.room_rate_plan import RoomRatePlan
from app.repositories.room_rate_plan import RoomRatePlanRepository
from app.schemas.room_rate_plan import RoomRatePlanCreate, RoomRatePlanRead, RoomRatePlanUpdate


class RoomRatePlanService:
    def __init__(self, db: AsyncSession):
        self.repo = RoomRatePlanRepository(db)
        self.db = db

    async def get_room_rate_plan_by_id(self, rate_plan_id: UUID) -> RoomRatePlan:
        """Lấy rate plan theo ID, ném 404 nếu không tồn tại"""
        return await self.repo.get_or_404(rate_plan_id, detail="Room rate plan không tồn tại")

    async def create_room_rate_plan(
        self, rate_plan_in: RoomRatePlanCreate
    ) -> RoomRatePlanRead:
        """Tạo room rate plan mới"""
        # Kiểm tra unique constraint: hotel_id + name
        existing = await self.repo.get_by_hotel_and_name(
            str(rate_plan_in.hotel_id), rate_plan_in.name
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Rate plan name đã tồn tại cho hotel này",
            )

        db_rate_plan = await self.repo.create(rate_plan_in)
        return RoomRatePlanRead.model_validate(db_rate_plan, from_attributes=True)

    async def get_room_rate_plans_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        hotel_id: UUID | None = None,
    ) -> dict[str, Any]:
        """Lấy danh sách room rate plans có phân trang và filter"""
        skip = (page - 1) * page_size

        filters = {}
        if hotel_id is not None:
            filters["hotel_id"] = hotel_id

        rate_plans = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [
                RoomRatePlanRead.model_validate(rp, from_attributes=True)
                for rp in rate_plans
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_room_rate_plan(
        self, rate_plan_id: UUID, rate_plan_in: RoomRatePlanUpdate
    ) -> RoomRatePlanRead:
        """Cập nhật room rate plan"""
        db_rate_plan = await self.get_room_rate_plan_by_id(rate_plan_id)

        # Kiểm tra unique constraint nếu name được cập nhật
        if rate_plan_in.name and rate_plan_in.name != db_rate_plan.name:
            hotel_id = (
                str(rate_plan_in.hotel_id)
                if rate_plan_in.hotel_id
                else str(db_rate_plan.hotel_id)
            )
            existing = await self.repo.get_by_hotel_and_name(hotel_id, rate_plan_in.name)
            if existing and existing.id != rate_plan_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Rate plan name đã tồn tại cho hotel này",
                )

        updated_rate_plan = await self.repo.update(db_rate_plan, rate_plan_in)
        return RoomRatePlanRead.model_validate(updated_rate_plan, from_attributes=True)

    async def delete_room_rate_plan(self, rate_plan_id: UUID) -> None:
        """Xóa room rate plan"""
        await self.repo.delete(rate_plan_id)

    async def search_room_rate_plans(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        """Tìm kiếm room rate plans theo name hoặc meal_plan"""
        skip = (page - 1) * page_size

        rate_plans = await self.repo.search(
            query=q,
            search_columns=["name", "meal_plan"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )

        total = await self.repo.count_search(
            query=q,
            search_columns=["name", "meal_plan"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [
                RoomRatePlanRead.model_validate(rp, from_attributes=True)
                for rp in rate_plans
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }


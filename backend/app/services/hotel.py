# app/services/hotel.py
from typing import Any
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.hotel import Hotel
from app.repositories.hotel import HotelRepository
from app.schemas.hotel import HotelCreate, HotelRead, HotelUpdate


class HotelService:
    def __init__(self, db: AsyncSession):
        self.repo = HotelRepository(db)
        self.db = db

    async def get_hotel_by_id(self, hotel_id: UUID) -> Hotel:
        """Lấy hotel theo ID, ném 404 nếu không tồn tại"""
        return await self.repo.get_or_404(hotel_id, detail="Hotel không tồn tại")

    async def create_hotel(self, hotel_in: HotelCreate) -> HotelRead:
        """Tạo hotel mới"""
        db_hotel = await self.repo.create(hotel_in)
        return HotelRead.model_validate(db_hotel, from_attributes=True)

    async def get_hotels_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        city_id: UUID | None = None,
        provider_id: UUID | None = None,
    ) -> dict[str, Any]:
        """Lấy danh sách hotels có phân trang và filter"""
        skip = (page - 1) * page_size

        filters = {}
        if city_id is not None:
            filters["city_id"] = city_id
        if provider_id is not None:
            filters["provider_id"] = provider_id

        hotels = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [HotelRead.model_validate(h, from_attributes=True) for h in hotels],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_hotel(self, hotel_id: UUID, hotel_in: HotelUpdate) -> HotelRead:
        """Cập nhật hotel"""
        db_hotel = await self.get_hotel_by_id(hotel_id)
        updated_hotel = await self.repo.update(db_hotel, hotel_in)
        return HotelRead.model_validate(updated_hotel, from_attributes=True)

    async def delete_hotel(self, hotel_id: UUID) -> None:
        """Xóa hotel"""
        await self.repo.delete(hotel_id)

    async def search_hotels(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        """Tìm kiếm hotels theo name hoặc address"""
        skip = (page - 1) * page_size

        hotels = await self.repo.search(
            query=q,
            search_columns=["name", "address"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )

        total = await self.repo.count_search(
            query=q,
            search_columns=["name", "address"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [HotelRead.model_validate(h, from_attributes=True) for h in hotels],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }


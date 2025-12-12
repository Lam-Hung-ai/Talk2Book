# app/services/hotel_room.py
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.hotel_room import HotelRoom
from app.repositories.hotel_room import HotelRoomRepository
from app.schemas.hotel_room import HotelRoomCreate, HotelRoomRead, HotelRoomUpdate


class HotelRoomService:
    def __init__(self, db: AsyncSession):
        self.repo = HotelRoomRepository(db)
        self.db = db

    async def get_hotel_room_by_id(self, room_id: UUID) -> HotelRoom:
        """Lấy room theo ID, ném 404 nếu không tồn tại"""
        return await self.repo.get_or_404(room_id, detail="Hotel room không tồn tại")

    async def create_hotel_room(self, room_in: HotelRoomCreate) -> HotelRoomRead:
        """Tạo hotel room mới"""
        # Kiểm tra unique constraint: hotel_id + code
        if room_in.code:
            existing = await self.repo.get_by_hotel_and_code(
                str(room_in.hotel_id), room_in.code
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Room code đã tồn tại cho hotel này",
                )

        db_room = await self.repo.create(room_in)
        return HotelRoomRead.model_validate(db_room, from_attributes=True)

    async def get_hotel_rooms_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        hotel_id: UUID | None = None,
    ) -> dict[str, Any]:
        """Lấy danh sách hotel rooms có phân trang và filter"""
        skip = (page - 1) * page_size

        filters = {}
        if hotel_id is not None:
            filters["hotel_id"] = hotel_id

        rooms = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [HotelRoomRead.model_validate(r, from_attributes=True) for r in rooms],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_hotel_room(
        self, room_id: UUID, room_in: HotelRoomUpdate
    ) -> HotelRoomRead:
        """Cập nhật hotel room"""
        db_room = await self.get_hotel_room_by_id(room_id)

        # Kiểm tra unique constraint nếu code được cập nhật
        if room_in.code and room_in.code != db_room.code:
            hotel_id = str(room_in.hotel_id) if room_in.hotel_id else str(db_room.hotel_id)
            existing = await self.repo.get_by_hotel_and_code(hotel_id, room_in.code)
            if existing and existing.id != room_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Room code đã tồn tại cho hotel này",
                )

        updated_room = await self.repo.update(db_room, room_in)
        return HotelRoomRead.model_validate(updated_room, from_attributes=True)

    async def delete_hotel_room(self, room_id: UUID) -> None:
        """Xóa hotel room"""
        await self.repo.delete(room_id)

    async def search_hotel_rooms(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        """Tìm kiếm hotel rooms theo code hoặc bed_config"""
        skip = (page - 1) * page_size

        rooms = await self.repo.search(
            query=q,
            search_columns=["code", "bed_config"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )

        total = await self.repo.count_search(
            query=q,
            search_columns=["code", "bed_config"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [HotelRoomRead.model_validate(r, from_attributes=True) for r in rooms],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }


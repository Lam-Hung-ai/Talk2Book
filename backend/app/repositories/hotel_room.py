# app/repositories/hotel_room.py
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.hotel_room import HotelRoom
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.hotel_room import HotelRoomCreate, HotelRoomUpdate


class HotelRoomRepository(
    BaseCRUD[HotelRoom, HotelRoomCreate, HotelRoomUpdate], SearchableRepository
):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, HotelRoom, db)
        SearchableRepository.__init__(self, HotelRoom, db)

    async def get_by_hotel_id(self, hotel_id: str, skip: int = 0, limit: int = 100):
        """Lấy danh sách room theo hotel_id"""
        return await self.get_multi(skip=skip, limit=limit, hotel_id=hotel_id)

    async def get_by_hotel_and_code(self, hotel_id: str, code: str) -> HotelRoom | None:
        """Tìm room theo hotel_id và code"""
        return (
            await self.db.exec(
                select(HotelRoom).where(
                    HotelRoom.hotel_id == hotel_id, HotelRoom.code == code
                )
            )
        ).first()

# app/repositories/hotel.py
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.hotel import Hotel
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.hotel import HotelCreate, HotelUpdate


class HotelRepository(BaseCRUD[Hotel, HotelCreate, HotelUpdate], SearchableRepository):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, Hotel, db)
        SearchableRepository.__init__(self, Hotel, db)

    async def get_by_name(self, name: str) -> Hotel | None:
        """Tìm hotel theo tên"""
        return (await self.db.exec(select(Hotel).where(Hotel.name == name))).first()

    async def get_by_city(self, city_id: str, skip: int = 0, limit: int = 100):
        """Lấy danh sách hotel theo city_id"""
        return await self.get_multi(skip=skip, limit=limit, city_id=city_id)

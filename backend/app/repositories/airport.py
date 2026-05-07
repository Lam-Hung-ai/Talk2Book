# app/repositories/airport.py
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.airport import Airport
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.airport import AirportCreate, AirportUpdate


class AirportRepository(
    BaseCRUD[Airport, AirportCreate, AirportUpdate], SearchableRepository
):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, Airport, db)
        SearchableRepository.__init__(self, Airport, db)

    async def get_by_iata(self, iata: str) -> Airport | None:
        """Tìm airport theo IATA code"""
        if not iata:
            return None
        return await self.db.get(Airport, iata.upper())

    async def get_by_icao(self, icao: str) -> Airport | None:
        """Tìm airport theo ICAO code"""
        if not icao:
            return None
        result = await self.db.exec(select(Airport).where(Airport.icao == icao.upper()))
        return result.first()

    async def get_by_city_id(
        self, city_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Airport]:
        """Lấy danh sách airports theo city_id"""
        result = await self.db.exec(
            select(Airport).where(Airport.city_id == city_id).offset(skip).limit(limit)
        )
        return list(result.all())

    async def get_by_city_id_and_name(self, city_id: UUID, name: str) -> Airport | None:
        """Tìm airport theo city_id và name (unique constraint)"""
        result = await self.db.exec(
            select(Airport).where(Airport.city_id == city_id, Airport.name == name)
        )
        return result.first()

# app/repositories/city.py
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.city import City
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.city import CityCreate, CityUpdate


class CityRepository(BaseCRUD[City, CityCreate, CityUpdate], SearchableRepository):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, City, db)
        SearchableRepository.__init__(self, City, db)

    async def get_by_country_code_and_name(self, country_code: str, name: str) -> City | None:
        """Tìm city theo country_code và name (unique constraint)"""
        result = await self.db.exec(
            select(City).where(
                City.country_code == country_code.upper(),
                City.name == name
            )
        )
        return result.first()

    async def get_by_country_code(self, country_code: str, skip: int = 0, limit: int = 100) -> list[City]:
        """Lấy danh sách cities theo country_code"""
        result = await self.db.exec(
            select(City)
            .where(City.country_code == country_code.upper())
            .offset(skip)
            .limit(limit)
        )
        return list(result.all())


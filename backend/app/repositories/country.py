# app/repositories/country.py
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.country import Country
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.country import CountryCreate, CountryUpdate


class CountryRepository(BaseCRUD[Country, CountryCreate, CountryUpdate], SearchableRepository):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, Country, db)
        SearchableRepository.__init__(self, Country, db)

    async def get_by_code(self, code: str) -> Country | None:
        """Tìm country theo code (primary key)"""
        return await self.db.get(Country, code.upper())


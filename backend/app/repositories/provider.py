# app/repositories/provider.py
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.provider import Provider
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.provider import ProviderCreate, ProviderUpdate


class ProviderRepository(
    BaseCRUD[Provider, ProviderCreate, ProviderUpdate], SearchableRepository
):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, Provider, db)
        SearchableRepository.__init__(self, Provider, db)

    async def get_by_display_name(self, display_name: str) -> Provider | None:
        result = await self.db.exec(
            select(Provider).where(Provider.display_name == display_name)
        )
        return result.first()

# app/repositories/price_quote.py

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.price_quote import PriceQuote
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.price_quote import PriceQuoteCreate, PriceQuoteUpdate


class PriceQuoteRepository(
    BaseCRUD[PriceQuote, PriceQuoteCreate, PriceQuoteUpdate], SearchableRepository
):
    """CRUD repository cho PriceQuote với khả năng tìm kiếm."""

    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, PriceQuote, db)
        SearchableRepository.__init__(self, PriceQuote, db)

    async def get_by_user(self, user_id: str, *, skip: int = 0, limit: int = 100):
        """Lấy tất cả price quotes của một user."""
        return await self.get_multi(skip=skip, limit=limit, user_id=user_id)

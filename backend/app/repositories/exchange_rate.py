# app/repositories/exchange_rate.py
from datetime import date

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.exchange_rate import ExchangeRate
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.exchange_rate import ExchangeRateCreate, ExchangeRateUpdate


class ExchangeRateRepository(BaseCRUD[ExchangeRate, ExchangeRateCreate, ExchangeRateUpdate], SearchableRepository):
    """CRUD repository cho ExchangeRate với khả năng tìm kiếm."""

    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, ExchangeRate, db)
        SearchableRepository.__init__(self, ExchangeRate, db)

    async def get_by_date_and_currencies(
        self, rate_date: date, base: str, quote: str
    ) -> ExchangeRate | None:
        """Tìm exchange rate theo ngày và cặp tiền tệ."""
        result = await self.db.exec(
            select(ExchangeRate).where(
                ExchangeRate.rate_date == rate_date,
                ExchangeRate.base == base,
                ExchangeRate.quote == quote,
            )
        )
        return result.first()

    async def get_by_date(self, rate_date: date, *, skip: int = 0, limit: int = 100):
        """Lấy tất cả exchange rates theo ngày."""
        return await self.get_multi(skip=skip, limit=limit, rate_date=rate_date)

    async def delete_by_composite_key(
        self, rate_date: date, base: str, quote: str
    ) -> None:
        """Xóa exchange rate theo composite primary key."""
        db_rate = await self.get_by_date_and_currencies(rate_date, base, quote)
        if not db_rate:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exchange rate không tồn tại",
            )
        await self.db.delete(db_rate)
        await self.db.commit()


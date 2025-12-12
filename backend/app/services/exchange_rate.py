# app/services/exchange_rate.py
from datetime import date
from typing import Any

from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.exchange_rate import ExchangeRateRepository
from app.schemas.exchange_rate import ExchangeRateCreate, ExchangeRateRead, ExchangeRateUpdate


class ExchangeRateService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ExchangeRateRepository(db)

    async def create_exchange_rate(self, rate_in: ExchangeRateCreate) -> ExchangeRateRead:
        """Tạo exchange rate mới."""
        # Kiểm tra base và quote phải khác nhau
        if rate_in.base == rate_in.quote:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Base currency và quote currency phải khác nhau",
            )

        # Kiểm tra đã tồn tại chưa
        existing = await self.repo.get_by_date_and_currencies(
            rate_in.rate_date, rate_in.base, rate_in.quote
        )
        if existing:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Exchange rate đã tồn tại cho ngày và cặp tiền tệ này",
            )

        rate = await self.repo.create(rate_in)
        return ExchangeRateRead.model_validate(rate, from_attributes=True)

    async def get_exchange_rate(
        self, rate_date: date, base: str, quote: str
    ) -> ExchangeRateRead:
        """Lấy exchange rate theo ngày và cặp tiền tệ."""
        rate = await self.repo.get_by_date_and_currencies(rate_date, base, quote)
        if not rate:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exchange rate không tồn tại",
            )
        return ExchangeRateRead.model_validate(rate, from_attributes=True)

    async def get_exchange_rates_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        rate_date: date | None = None,
        base: str | None = None,
        quote: str | None = None,
    ) -> dict[str, Any]:
        """Lấy danh sách exchange rates có phân trang và filter."""
        skip = (page - 1) * page_size

        filters: dict[str, Any] = {}
        if rate_date is not None:
            filters["rate_date"] = rate_date
        if base is not None:
            filters["base"] = base
        if quote is not None:
            filters["quote"] = quote

        rates = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [ExchangeRateRead.model_validate(r, from_attributes=True) for r in rates],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_exchange_rate(
        self, rate_date: date, base: str, quote: str, rate_in: ExchangeRateUpdate
    ) -> ExchangeRateRead:
        """Cập nhật exchange rate."""
        db_rate = await self.repo.get_by_date_and_currencies(rate_date, base, quote)
        if not db_rate:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exchange rate không tồn tại",
            )

        updated = await self.repo.update(db_rate, rate_in)
        return ExchangeRateRead.model_validate(updated, from_attributes=True)

    async def delete_exchange_rate(self, rate_date: date, base: str, quote: str) -> None:
        """Xóa exchange rate."""
        await self.repo.delete_by_composite_key(rate_date, base, quote)

    async def search_exchange_rates(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        """Tìm kiếm exchange rates theo base hoặc quote."""
        skip = (page - 1) * page_size

        rates = await self.repo.search(
            query=q,
            search_columns=["base", "quote"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )

        total = await self.repo.count_search(
            query=q,
            search_columns=["base", "quote"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [ExchangeRateRead.model_validate(r, from_attributes=True) for r in rates],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }


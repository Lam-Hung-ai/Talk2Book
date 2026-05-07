# app/services/price_quote.py
from typing import Any
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.price_quote import PriceQuoteRepository
from app.schemas.price_quote import PriceQuoteCreate, PriceQuoteRead, PriceQuoteUpdate


class PriceQuoteService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PriceQuoteRepository(db)

    async def create_price_quote(self, quote_in: PriceQuoteCreate) -> PriceQuoteRead:
        """Tạo price quote mới."""
        quote = await self.repo.create(quote_in)
        return PriceQuoteRead.model_validate(quote, from_attributes=True)

    async def get_price_quote(self, quote_id: UUID) -> PriceQuoteRead:
        """Lấy price quote theo ID."""
        quote = await self.repo.get_or_404(quote_id, detail="Price quote không tồn tại")
        return PriceQuoteRead.model_validate(quote, from_attributes=True)

    async def get_price_quotes_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        user_id: str | None = None,
        vertical: str | None = None,
        currency_code: str | None = None,
    ) -> dict[str, Any]:
        """Lấy danh sách price quotes có phân trang và filter."""
        skip = (page - 1) * page_size

        filters: dict[str, Any] = {}
        if user_id is not None:
            filters["user_id"] = user_id
        if vertical is not None:
            filters["vertical"] = vertical
        if currency_code is not None:
            filters["currency_code"] = currency_code

        quotes = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [
                PriceQuoteRead.model_validate(q, from_attributes=True) for q in quotes
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_price_quote(
        self, quote_id: UUID, quote_in: PriceQuoteUpdate
    ) -> PriceQuoteRead:
        """Cập nhật price quote."""
        db_quote = await self.repo.get_or_404(
            quote_id, detail="Price quote không tồn tại"
        )
        updated = await self.repo.update(db_quote, quote_in)
        return PriceQuoteRead.model_validate(updated, from_attributes=True)

    async def delete_price_quote(self, quote_id: UUID) -> None:
        """Xóa price quote."""
        await self.repo.delete(quote_id)

    async def search_price_quotes(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        """Tìm kiếm price quotes theo vertical."""
        skip = (page - 1) * page_size

        quotes = await self.repo.search(
            query=q,
            search_columns=["vertical"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )

        total = await self.repo.count_search(
            query=q,
            search_columns=["vertical"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [
                PriceQuoteRead.model_validate(q, from_attributes=True) for q in quotes
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

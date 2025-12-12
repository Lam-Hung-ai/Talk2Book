# app/services/tax.py
from typing import Any
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.tax import TaxRepository
from app.schemas.tax import TaxCreate, TaxRead, TaxUpdate


class TaxService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TaxRepository(db)

    async def create_tax(self, tax_in: TaxCreate) -> TaxRead:
        """Tạo tax mới."""
        tax = await self.repo.create(tax_in)
        return TaxRead.model_validate(tax, from_attributes=True)

    async def get_tax(self, tax_id: UUID) -> TaxRead:
        """Lấy tax theo ID."""
        tax = await self.repo.get_or_404(tax_id, detail="Tax không tồn tại")
        return TaxRead.model_validate(tax, from_attributes=True)

    async def get_taxes_paginated(
        self,
        page: int = 1,
        page_size: int = 50,
        scope: str | None = None,
        currency_code: str | None = None,
    ) -> dict[str, Any]:
        """Lấy danh sách taxes có phân trang và filter."""
        skip = (page - 1) * page_size

        filters: dict[str, Any] = {}
        if scope is not None:
            filters["scope"] = scope
        if currency_code is not None:
            filters["currency_code"] = currency_code

        taxes = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [TaxRead.model_validate(t, from_attributes=True) for t in taxes],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_tax(self, tax_id: UUID, tax_in: TaxUpdate) -> TaxRead:
        """Cập nhật tax."""
        db_tax = await self.repo.get_or_404(tax_id, detail="Tax không tồn tại")
        updated = await self.repo.update(db_tax, tax_in)
        return TaxRead.model_validate(updated, from_attributes=True)

    async def delete_tax(self, tax_id: UUID) -> None:
        """Xóa tax."""
        await self.repo.delete(tax_id)

    async def search_taxes(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        """Tìm kiếm taxes theo name hoặc scope."""
        skip = (page - 1) * page_size

        taxes = await self.repo.search(
            query=q,
            search_columns=["name", "scope"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )

        total = await self.repo.count_search(
            query=q,
            search_columns=["name", "scope"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [TaxRead.model_validate(t, from_attributes=True) for t in taxes],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }


# app/services/country.py
from typing import Any

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.country import Country
from app.models.currency import Currency
from app.repositories.country import CountryRepository
from app.schemas.country import CountryCreate, CountryRead, CountryUpdate


class CountryService:
    def __init__(self, db: AsyncSession):
        self.repo = CountryRepository(db)
        self.db = db

    async def get_country_by_code(self, code: str) -> Country:
        """Lấy country theo code, ném 404 nếu không tồn tại"""
        country = await self.repo.get_by_code(code.upper())
        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Country with code '{code}' không tồn tại"
            )
        return country

    async def create_country(self, country_in: CountryCreate) -> CountryRead:
        """Tạo country mới"""
        # Kiểm tra code đã tồn tại chưa
        if await self.repo.get_by_code(country_in.code.upper()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Country code '{country_in.code}' đã tồn tại"
            )

        # Kiểm tra currency_code có tồn tại không
        currency_code_upper = country_in.currency_code.upper()
        currency = await self.db.get(Currency, currency_code_upper)
        if not currency:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Currency code '{country_in.currency_code}' không tồn tại"
            )

        country_data = country_in.model_dump()
        country_data["code"] = country_data["code"].upper()
        country_data["currency_code"] = currency_code_upper

        db_country = await self.repo.create(country_data)
        return CountryRead.model_validate(db_country, from_attributes=True)

    async def get_countries_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Lấy danh sách countries có phân trang"""
        skip = (page - 1) * page_size

        countries = await self.repo.get_multi(skip=skip, limit=page_size)
        total = await self.repo.get_count()

        return {
            "items": [CountryRead.model_validate(c, from_attributes=True) for c in countries],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def update_country(self, code: str, country_in: CountryUpdate) -> CountryRead:
        """Cập nhật country"""
        db_country = await self.get_country_by_code(code)

        update_data = country_in.model_dump(exclude_unset=True)
        if "currency_code" in update_data:
            currency_code_upper = update_data["currency_code"].upper()
            # Kiểm tra currency_code có tồn tại không
            currency = await self.db.get(Currency, currency_code_upper)
            if not currency:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Currency code '{update_data['currency_code']}' không tồn tại"
                )
            update_data["currency_code"] = currency_code_upper

        updated_country = await self.repo.update(db_country, update_data)
        return CountryRead.model_validate(updated_country, from_attributes=True)

    async def delete_country(self, code: str) -> None:
        """Xóa country"""
        country = await self.get_country_by_code(code)
        await self.repo.delete(country.code)

    async def search_countries(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False
    ) -> dict[str, Any]:
        """Tìm kiếm countries theo code hoặc name"""
        skip = (page - 1) * page_size

        countries = await self.repo.search(
            query=q,
            search_columns=["code", "name"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size
        )

        total = await self.repo.count_search(
            query=q,
            search_columns=["code", "name"],
            exact_match=exact_match,
            case_sensitive=case_sensitive
        )

        return {
            "items": [CountryRead.model_validate(c, from_attributes=True) for c in countries],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }


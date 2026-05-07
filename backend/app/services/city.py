# app/services/city.py
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.city import City
from app.models.country import Country
from app.repositories.city import CityRepository
from app.schemas.city import CityCreate, CityRead, CityUpdate


class CityService:
    def __init__(self, db: AsyncSession):
        self.repo = CityRepository(db)
        self.db = db

    async def get_city_by_id(self, city_id: UUID) -> City:
        """Lấy city theo ID, ném 404 nếu không tồn tại"""
        return await self.repo.get_or_404(city_id, detail="City không tồn tại")

    async def create_city(self, city_in: CityCreate) -> CityRead:
        """Tạo city mới"""
        # Kiểm tra country_code có tồn tại không
        country_code_upper = city_in.country_code.upper()
        country = await self.db.get(Country, country_code_upper)
        if not country:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Country code '{city_in.country_code}' không tồn tại",
            )

        # Kiểm tra unique constraint (country_code, name)
        if await self.repo.get_by_country_code_and_name(
            country_code_upper, city_in.name
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"City '{city_in.name}' đã tồn tại trong country '{country_code_upper}'",
            )

        city_data = city_in.model_dump()
        city_data["country_code"] = country_code_upper

        db_city = await self.repo.create(city_data)
        return CityRead.model_validate(db_city, from_attributes=True)

    async def get_cities_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        country_code: str | None = None,
    ) -> dict[str, Any]:
        """Lấy danh sách cities có phân trang và filter"""
        skip = (page - 1) * page_size

        if country_code:
            cities = await self.repo.get_by_country_code(
                country_code.upper(), skip=skip, limit=page_size
            )
            # Đếm tổng số cities của country
            all_cities = await self.repo.get_by_country_code(
                country_code.upper(), skip=0, limit=10000
            )
            total = len(all_cities)
        else:
            filters = {}
            cities = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
            total = await self.repo.get_count(**filters)

        return {
            "items": [CityRead.model_validate(c, from_attributes=True) for c in cities],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_city(self, city_id: UUID, city_in: CityUpdate) -> CityRead:
        """Cập nhật city"""
        db_city = await self.get_city_by_id(city_id)

        update_data = city_in.model_dump(exclude_unset=True)

        # Kiểm tra country_code nếu có update
        if "country_code" in update_data:
            country_code_upper = update_data["country_code"].upper()
            country = await self.db.get(Country, country_code_upper)
            if not country:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Country code '{update_data['country_code']}' không tồn tại",
                )
            update_data["country_code"] = country_code_upper

        # Kiểm tra unique constraint nếu có update name hoặc country_code
        if "name" in update_data or "country_code" in update_data:
            final_country_code = update_data.get(
                "country_code", db_city.country_code
            ).upper()
            final_name = update_data.get("name", db_city.name)
            existing_city = await self.repo.get_by_country_code_and_name(
                final_country_code, final_name
            )
            if existing_city and existing_city.id != city_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"City '{final_name}' đã tồn tại trong country '{final_country_code}'",
                )

        updated_city = await self.repo.update(db_city, update_data)
        return CityRead.model_validate(updated_city, from_attributes=True)

    async def delete_city(self, city_id: UUID) -> None:
        """Xóa city"""
        await self.repo.delete(city_id)

    async def search_cities(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        """Tìm kiếm cities theo name hoặc country_code"""
        skip = (page - 1) * page_size

        cities = await self.repo.search(
            query=q,
            search_columns=["name", "country_code"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )

        total = await self.repo.count_search(
            query=q,
            search_columns=["name", "country_code"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [CityRead.model_validate(c, from_attributes=True) for c in cities],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

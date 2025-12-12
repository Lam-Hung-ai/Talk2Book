# app/services/provider.py
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.provider import Provider
from app.repositories.provider import ProviderRepository
from app.schemas.provider import ProviderCreate, ProviderRead, ProviderUpdate


class ProviderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProviderRepository(db)

    async def create_provider(self, provider_in: ProviderCreate) -> ProviderRead:
        existing = await self.repo.get_by_display_name(provider_in.display_name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Display name đã tồn tại",
            )
        provider = await self.repo.create(provider_in)
        return ProviderRead.model_validate(provider, from_attributes=True)

    async def get_provider(self, provider_id: UUID) -> ProviderRead:
        provider = await self.repo.get_or_404(provider_id, detail="Provider không tồn tại")
        return ProviderRead.model_validate(provider, from_attributes=True)

    async def get_providers_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        type_filter: str | None = None,
        country_code: str | None = None,
        status_filter: str | None = None,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size

        filters: dict[str, Any] = {}
        if type_filter:
            filters["type"] = type_filter
        if country_code:
            filters["country_code"] = country_code
        if status_filter:
            filters["status"] = status_filter

        providers = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [ProviderRead.model_validate(p, from_attributes=True) for p in providers],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_provider(self, provider_id: UUID, provider_in: ProviderUpdate) -> ProviderRead:
        db_provider = await self.repo.get_or_404(provider_id, detail="Provider không tồn tại")
        updated = await self.repo.update(db_provider, provider_in)
        return ProviderRead.model_validate(updated, from_attributes=True)

    async def delete_provider(self, provider_id: UUID) -> None:
        await self.repo.delete(provider_id)

    async def search_providers(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False,
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size
        search_columns = ["legal_name", "display_name", "country_code"]

        providers = await self.repo.search(
            query=q,
            search_columns=search_columns,
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size,
        )
        total = await self.repo.count_search(
            query=q,
            search_columns=search_columns,
            exact_match=exact_match,
            case_sensitive=case_sensitive,
        )

        return {
            "items": [ProviderRead.model_validate(p, from_attributes=True) for p in providers],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }


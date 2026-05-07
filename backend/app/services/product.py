# app/services/product.py
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.provider import Provider
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProductRepository(db)

    async def _ensure_provider(self, provider_id: UUID) -> None:
        provider = await self.db.get(Provider, provider_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider {provider_id} does not exist",
            )

    async def create_product(self, payload: ProductCreate) -> ProductRead:
        await self._ensure_provider(payload.provider_id)
        product = await self.repo.create(payload)
        return ProductRead.model_validate(product, from_attributes=True)

    async def list_products(
        self,
        page: int = 1,
        page_size: int = 20,
        q: str | None = None,
        provider_id: UUID | None = None,
        type: str | None = None,
    ) -> dict[str, object]:
        skip = (page - 1) * page_size

        if q:
            items = await self.repo.search(
                query=q,
                search_columns=["title"],
                skip=skip,
                limit=page_size,
                exact_match=False,
                case_sensitive=False,
            )
            total = await self.repo.count_search(
                query=q,
                search_columns=["title"],
                exact_match=False,
                case_sensitive=False,
            )
        else:
            filters = {}
            if provider_id:
                filters["provider_id"] = provider_id
            if type:
                filters["type"] = type

            items = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
            total = await self.repo.get_count(**filters)

        return {
            "items": [
                ProductRead.model_validate(p, from_attributes=True) for p in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def get_product(self, product_id: UUID) -> ProductRead:
        product = await self.repo.get_or_404(product_id, detail="Product not found")
        return ProductRead.model_validate(product, from_attributes=True)

    async def update_product(
        self, product_id: UUID, payload: ProductUpdate
    ) -> ProductRead:
        product = await self.repo.get_or_404(product_id, detail="Product not found")
        data = payload.model_dump(exclude_unset=True)

        if "provider_id" in data:
            await self._ensure_provider(data["provider_id"])

        updated = await self.repo.update(product, data)
        return ProductRead.model_validate(updated, from_attributes=True)

    async def delete_product(self, product_id: UUID) -> None:
        await self.repo.delete(product_id)

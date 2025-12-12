# app/services/product.py
from typing import Any
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.product import Product
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate


class ProductService:
    def __init__(self, db: AsyncSession):
        self.repo = ProductRepository(db)
        self.db = db

    async def get_product_by_id(self, product_id: UUID) -> Product:
        """Lấy product theo ID, ném 404 nếu không tồn tại"""
        return await self.repo.get_or_404(product_id, detail="Product không tồn tại")

    async def create_product(self, product_in: ProductCreate) -> ProductRead:
        """Tạo product mới"""
        db_product = await self.repo.create(product_in)
        return ProductRead.model_validate(db_product, from_attributes=True)

    async def get_products_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        provider_id: UUID | None = None,
        city_id: UUID | None = None,
    ) -> dict[str, Any]:
        """Lấy danh sách products có phân trang và filter"""
        skip = (page - 1) * page_size

        filters = {}
        if provider_id is not None:
            filters["provider_id"] = provider_id
        if city_id is not None:
            filters["city_id"] = city_id

        products = await self.repo.get_multi(skip=skip, limit=page_size, **filters)
        total = await self.repo.get_count(**filters)

        return {
            "items": [ProductRead.model_validate(p, from_attributes=True) for p in products],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def update_product(self, product_id: UUID, product_in: ProductUpdate) -> ProductRead:
        """Cập nhật product"""
        db_product = await self.get_product_by_id(product_id)
        updated_product = await self.repo.update(db_product, product_in)
        return ProductRead.model_validate(updated_product, from_attributes=True)

    async def delete_product(self, product_id: UUID) -> None:
        """Xóa product"""
        await self.repo.delete(product_id)

    async def search_products(
        self,
        q: str,
        page: int = 1,
        page_size: int = 20,
        exact_match: bool = False,
        case_sensitive: bool = False
    ) -> dict[str, Any]:
        """Tìm kiếm products theo title"""
        skip = (page - 1) * page_size

        products = await self.repo.search(
            query=q,
            search_columns=["title"],
            exact_match=exact_match,
            case_sensitive=case_sensitive,
            skip=skip,
            limit=page_size
        )

        total = await self.repo.count_search(
            query=q,
            search_columns=["title"],
            exact_match=exact_match,
            case_sensitive=case_sensitive
        )

        return {
            "items": [ProductRead.model_validate(p, from_attributes=True) for p in products],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }


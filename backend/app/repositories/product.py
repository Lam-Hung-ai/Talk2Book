# app/repositories/product.py
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.product import Product
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository(BaseCRUD[Product, ProductCreate, ProductUpdate], SearchableRepository):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, Product, db)
        SearchableRepository.__init__(self, Product, db)

    async def get_by_provider_id(self, provider_id: UUID) -> list[Product]:
        """Lấy danh sách products theo provider_id"""
        result = await self.db.exec(select(Product).where(Product.provider_id == provider_id))
        return list(result.all())

    async def get_by_city_id(self, city_id: UUID) -> list[Product]:
        """Lấy danh sách products theo city_id"""
        result = await self.db.exec(select(Product).where(Product.city_id == city_id))
        return list(result.all())


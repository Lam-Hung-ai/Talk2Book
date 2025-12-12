# app/repositories/product.py
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

    async def get_by_provider(self, provider_id: str):
        """Lấy danh sách products theo provider_id"""
        stmt = select(Product).where(Product.provider_id == provider_id)
        result = await self.db.exec(stmt)
        return result.all()

    async def get_by_city(self, city_id: str):
        """Lấy danh sách products theo city_id"""
        stmt = select(Product).where(Product.city_id == city_id)
        result = await self.db.exec(stmt)
        return result.all()


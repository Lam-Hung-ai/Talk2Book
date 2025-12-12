# app/repositories/tax.py
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.tax import Tax
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.tax import TaxCreate, TaxUpdate


class TaxRepository(BaseCRUD[Tax, TaxCreate, TaxUpdate], SearchableRepository):
    """CRUD repository cho Tax với khả năng tìm kiếm."""

    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, Tax, db)
        SearchableRepository.__init__(self, Tax, db)


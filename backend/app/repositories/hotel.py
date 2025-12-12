# app/repositories/hotel.py
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.hotel import Hotel
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.hotel import HotelCreate, HotelUpdate


class HotelRepository(BaseCRUD[Hotel, HotelCreate, HotelUpdate], SearchableRepository):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, Hotel, db)
        SearchableRepository.__init__(self, Hotel, db)


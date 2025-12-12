# app/repositories/hotel_room.py
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.hotel_room import HotelRoom
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.hotel_room import HotelRoomCreate, HotelRoomUpdate


class HotelRoomRepository(BaseCRUD[HotelRoom, HotelRoomCreate, HotelRoomUpdate], SearchableRepository):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, HotelRoom, db)
        SearchableRepository.__init__(self, HotelRoom, db)


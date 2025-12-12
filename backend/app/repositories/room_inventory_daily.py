# app/repositories/room_inventory_daily.py
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.room_inventory_daily import RoomInventoryDaily
from app.repositories.base import BaseCRUD
from app.schemas.room_inventory_daily import RoomInventoryDailyCreate, RoomInventoryDailyUpdate


class RoomInventoryDailyRepository(BaseCRUD[RoomInventoryDaily, RoomInventoryDailyCreate, RoomInventoryDailyUpdate]):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, RoomInventoryDaily, db)


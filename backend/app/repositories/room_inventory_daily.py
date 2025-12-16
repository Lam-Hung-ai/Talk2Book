# app/repositories/room_inventory_daily.py
from datetime import date

from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.room_inventory_daily import RoomInventoryDaily
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.room_inventory_daily import (
    RoomInventoryDailyCreate,
    RoomInventoryDailyUpdate,
)


class RoomInventoryDailyRepository(BaseCRUD[RoomInventoryDaily, RoomInventoryDailyCreate, RoomInventoryDailyUpdate], SearchableRepository):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, RoomInventoryDaily, db)
        SearchableRepository.__init__(self, RoomInventoryDaily, db)

    async def get_by_room_and_rate_plan(
        self, room_id: str, rate_plan_id: str, skip: int = 0, limit: int = 100
    ):
        """Lấy danh sách inventory theo room_id và rate_plan_id"""
        return await self.get_multi(skip=skip, limit=limit, room_id=room_id, rate_plan_id=rate_plan_id)

    async def get_by_date_range(
        self, stay_date_from: date, stay_date_to: date, skip: int = 0, limit: int = 100
    ):
        """Lấy danh sách inventory theo khoảng ngày"""
        query = select(RoomInventoryDaily).where(
            and_(
                RoomInventoryDaily.stay_date >= stay_date_from,
                RoomInventoryDaily.stay_date <= stay_date_to,
            )
        )
        query = query.offset(skip).limit(limit)
        result = await self.db.exec(query)
        return result.all()

    async def get_by_room_rate_date(
        self, room_id: str, rate_plan_id: str, stay_date: date
    ) -> RoomInventoryDaily | None:
        """Tìm inventory theo room_id, rate_plan_id và stay_date (composite key)"""
        return (
            await self.db.exec(
                select(RoomInventoryDaily).where(
                    and_(
                        RoomInventoryDaily.room_id == room_id,
                        RoomInventoryDaily.rate_plan_id == rate_plan_id,
                        RoomInventoryDaily.stay_date == stay_date,
                    )
                )
            )
        ).first()


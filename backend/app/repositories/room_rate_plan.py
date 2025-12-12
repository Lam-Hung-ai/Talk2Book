# app/repositories/room_rate_plan.py
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.room_rate_plan import RoomRatePlan
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.room_rate_plan import RoomRatePlanCreate, RoomRatePlanUpdate


class RoomRatePlanRepository(BaseCRUD[RoomRatePlan, RoomRatePlanCreate, RoomRatePlanUpdate], SearchableRepository):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, RoomRatePlan, db)
        SearchableRepository.__init__(self, RoomRatePlan, db)

    async def get_by_hotel_id(self, hotel_id: str, skip: int = 0, limit: int = 100):
        """Lấy danh sách rate plan theo hotel_id"""
        return await self.get_multi(skip=skip, limit=limit, hotel_id=hotel_id)

    async def get_by_hotel_and_name(self, hotel_id: str, name: str) -> RoomRatePlan | None:
        """Tìm rate plan theo hotel_id và name"""
        return (
            await self.db.exec(
                select(RoomRatePlan).where(
                    RoomRatePlan.hotel_id == hotel_id, RoomRatePlan.name == name
                )
            )
        ).first()


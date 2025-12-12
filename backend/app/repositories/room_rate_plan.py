# app/repositories/room_rate_plan.py
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.room_rate_plan import RoomRatePlan
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.room_rate_plan import RoomRatePlanCreate, RoomRatePlanUpdate


class RoomRatePlanRepository(BaseCRUD[RoomRatePlan, RoomRatePlanCreate, RoomRatePlanUpdate], SearchableRepository):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, RoomRatePlan, db)
        SearchableRepository.__init__(self, RoomRatePlan, db)


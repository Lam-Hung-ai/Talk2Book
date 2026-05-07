from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.flight_schedule import FlightSchedule
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.flight_schedule import FlightScheduleCreate, FlightScheduleUpdate


class FlightScheduleRepository(
    BaseCRUD[FlightSchedule, FlightScheduleCreate, FlightScheduleUpdate],
    SearchableRepository,
):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, FlightSchedule, db)
        SearchableRepository.__init__(self, FlightSchedule, db)

    async def list_filtered(
        self,
        *,
        limit: int,
        offset: int,
        provider_id: UUID | None = None,
        route_id: UUID | None = None,
        dow: int | str | None = None,
    ):
        stmt = select(FlightSchedule)
        if provider_id:
            stmt = stmt.where(FlightSchedule.provider_id == provider_id)
        if route_id:
            stmt = stmt.where(FlightSchedule.route_id == route_id)
        if dow is not None:
            dow_str = f"{int(dow):07b}" if isinstance(dow, int) else str(dow)
            stmt = stmt.where(FlightSchedule.dow == dow_str)

        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.exec(stmt)
        return result.all()

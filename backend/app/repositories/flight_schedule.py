from collections.abc import Sequence
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
        provider_id: UUID | None,
        route_id: UUID | None,
        dow: int | None,
    ) -> Sequence[FlightSchedule]:
        query = select(FlightSchedule)
        if provider_id:
            query = query.where(FlightSchedule.provider_id == provider_id)
        if route_id:
            query = query.where(FlightSchedule.route_id == route_id)
        if dow is not None:
            # check if dow bitstring contains 1 at index dow (0=Mon)
            pattern = f"_{dow}_"
            query = query.where(FlightSchedule.dow.ilike(f"%{pattern}%") | FlightSchedule.dow.ilike(f"%{dow}%"))
        result = await self.db.exec(query.offset(offset).limit(limit))
        return result.all()


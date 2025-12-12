from datetime import date
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.flight_instance import FlightInstance
from app.repositories.base import BaseCRUD
from app.repositories.searchable import SearchableRepository
from app.schemas.flight_instance import FlightInstanceCreate, FlightInstanceUpdate


class FlightInstanceRepository(
    BaseCRUD[FlightInstance, FlightInstanceCreate, FlightInstanceUpdate],
    SearchableRepository,
):
    def __init__(self, db: AsyncSession):
        BaseCRUD.__init__(self, FlightInstance, db)
        SearchableRepository.__init__(self, FlightInstance, db)

    async def list_filtered(
        self,
        *,
        limit: int,
        offset: int,
        schedule_id: UUID | None = None,
        flight_date: date | None = None,
        status: str | None = None,
    ):
        stmt = select(FlightInstance)
        if schedule_id:
            stmt = stmt.where(FlightInstance.schedule_id == schedule_id)
        if flight_date:
            stmt = stmt.where(FlightInstance.flight_date == flight_date)
        if status:
            stmt = stmt.where(FlightInstance.status == status)

        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.exec(stmt)
        return result.all()


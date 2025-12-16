from uuid import UUID

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.seat_inventory import SeatInventory
from app.repositories.searchable import SearchableRepository
from app.schemas.seat_inventory import SeatInventoryCreate, SeatInventoryUpdate


class SeatInventoryRepository(SearchableRepository):
    def __init__(self, db: AsyncSession):
        self.model = SeatInventory
        self.db = db
        SearchableRepository.__init__(self, SeatInventory, db)

    async def get(self, instance_id: UUID, cabin, fare_bucket) -> SeatInventory | None:
        stmt = select(SeatInventory).where(
            SeatInventory.instance_id == instance_id,
            SeatInventory.cabin == cabin,
            SeatInventory.fare_bucket == fare_bucket,
        )
        result = await self.db.exec(stmt)
        return result.first()

    async def get_count(self) -> int:
        result = await self.db.exec(select(func.count()).select_from(SeatInventory))
        return result.one()

    async def create(self, obj_in: SeatInventoryCreate | dict) -> SeatInventory:
        db_obj = self.model.model_validate(obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self, db_obj: SeatInventory, obj_in: SeatInventoryUpdate | dict
    ) -> SeatInventory:
        update_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        )
        for key, value in update_data.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, instance_id: UUID, cabin, fare_bucket) -> bool:
        obj = await self.get(instance_id, cabin, fare_bucket)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True


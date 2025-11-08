from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.slot_inventory import SlotInventory


class SlotInventoryCRUD:
    """CRUD operations for SlotInventory"""

    @staticmethod
    def create(
        session: Session,
        time_slot_id: UUID,
        total: int,
        sold: int,
        price: float,
        currency_code: str,
    ) -> SlotInventory:
        si = SlotInventory(
            time_slot_id=time_slot_id,
            total=total,
            sold=sold,
            price=price,
            currency_code=currency_code,
            updated_at=datetime.utcnow(),
        )
        session.add(si)
        session.commit()
        session.refresh(si)
        return si

    @staticmethod
    def get_by_id(session: Session, time_slot_id: UUID) -> Optional[SlotInventory]:
        return session.get(SlotInventory, time_slot_id)

    @staticmethod
    def get_by_time_slot(session: Session, time_slot_id: UUID) -> Optional[SlotInventory]:
        return session.get(SlotInventory, time_slot_id)

    @staticmethod
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[SlotInventory]:
        statement = select(SlotInventory).offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def update(
        session: Session,
        time_slot_id: UUID,
        total: Optional[int] = None,
        sold: Optional[int] = None,
        price: Optional[float] = None,
    ) -> Optional[SlotInventory]:
        si = session.get(SlotInventory, time_slot_id)
        if not si:
            return None
        if total is not None:
            si.total = total
        if sold is not None:
            si.sold = sold
        if price is not None:
            si.price = price
        si.updated_at = datetime.utcnow()
        session.add(si)
        session.commit()
        session.refresh(si)
        return si

    @staticmethod
    def delete(session: Session, time_slot_id: UUID) -> bool:
        si = session.get(SlotInventory, time_slot_id)
        if not si:
            return False
        session.delete(si)
        session.commit()
        return True

from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.booking_items import BookingItem


class BookingItemCRUD:
    """CRUD operations for BookingItem"""

    @staticmethod
    def create(
        session: Session,
        booking_id: UUID,
        product_id: Optional[UUID],
        time_slot_id: Optional[UUID],
        quantity: int,
        unit_price: float,
        currency_code: Optional[str],
        total_amount: float,
        snapshot: Optional[dict] = None,
    ) -> BookingItem:
        item = BookingItem(
            booking_id=booking_id,
            product_id=product_id,
            time_slot_id=time_slot_id,
            quantity=quantity,
            unit_price=unit_price,
            currency_code=currency_code,
            total_amount=total_amount,
            snapshot=snapshot,
            created_at=datetime.utcnow(),
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    @staticmethod
    def get_by_id(session: Session, item_id: UUID) -> Optional[BookingItem]:
        return session.get(BookingItem, item_id)

    @staticmethod
    def get_by_booking(
        session: Session,
        booking_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[BookingItem]:
        statement = select(BookingItem).where(BookingItem.booking_id == booking_id)
        statement = statement.offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[BookingItem]:
        statement = select(BookingItem).offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def update(
        session: Session,
        item_id: UUID,
        quantity: Optional[int] = None,
        unit_price: Optional[float] = None,
        total_amount: Optional[float] = None,
        snapshot: Optional[dict] = None,
    ) -> Optional[BookingItem]:
        item = session.get(BookingItem, item_id)
        if not item:
            return None
        if quantity is not None:
            item.quantity = quantity
        if unit_price is not None:
            item.unit_price = unit_price
        if total_amount is not None:
            item.total_amount = total_amount
        if snapshot is not None:
            item.snapshot = snapshot
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    @staticmethod
    def delete(session: Session, item_id: UUID) -> bool:
        item = session.get(BookingItem, item_id)
        if not item:
            return False
        session.delete(item)
        session.commit()
        return True

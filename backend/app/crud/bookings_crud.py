from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.bookings import Booking


class BookingCRUD:
    """CRUD operations for Booking"""

    @staticmethod
    def create(
        session: Session,
        user_id: Optional[UUID] = None,
        status: str = "created",
        total_amount: float = 0.0,
        currency_code: Optional[str] = None,
        quote_id: Optional[UUID] = None,
        payment_method: Optional[str] = None,
    ) -> Booking:
        booking = Booking(
            user_id=user_id,
            status=status,
            total_amount=total_amount,
            currency_code=currency_code,
            quote_id=quote_id,
            payment_method=payment_method,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(booking)
        session.commit()
        session.refresh(booking)
        return booking

    @staticmethod
    def get_by_id(session: Session, booking_id: UUID) -> Optional[Booking]:
        return session.get(Booking, booking_id)

    @staticmethod
    def get_by_user(
        session: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Booking]:
        statement = select(Booking).where(Booking.user_id == user_id)
        statement = statement.offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Booking]:
        statement = select(Booking).offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def update(
        session: Session,
        booking_id: UUID,
        status: Optional[str] = None,
        total_amount: Optional[float] = None,
        payment_method: Optional[str] = None,
    ) -> Optional[Booking]:
        booking = session.get(Booking, booking_id)
        if not booking:
            return None
        if status is not None:
            booking.status = status
        if total_amount is not None:
            booking.total_amount = total_amount
        if payment_method is not None:
            booking.payment_method = payment_method
        booking.updated_at = datetime.utcnow()
        session.add(booking)
        session.commit()
        session.refresh(booking)
        return booking

    @staticmethod
    def delete(session: Session, booking_id: UUID) -> bool:
        booking = session.get(Booking, booking_id)
        if not booking:
            return False
        session.delete(booking)
        session.commit()
        return True

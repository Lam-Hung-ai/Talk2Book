from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.models.passengers import Passenger


class PassengerCRUD:
    """CRUD operations for Passenger"""

    @staticmethod
    def create(
        session: Session,
        booking_id: UUID,
        full_name: str,
        birthdate: Optional[date] = None,
        nationality: Optional[str] = None,
        passenger_type: Optional[str] = None,
        document_type: Optional[str] = None,
        document_number: Optional[str] = None,
    ) -> Passenger:
        p = Passenger(
            booking_id=booking_id,
            full_name=full_name,
            birthdate=birthdate,
            nationality=nationality,
            passenger_type=passenger_type,
            document_type=document_type,
            document_number=document_number,
        )
        session.add(p)
        session.commit()
        session.refresh(p)
        return p

    @staticmethod
    def get_by_id(session: Session, passenger_id: UUID) -> Optional[Passenger]:
        return session.get(Passenger, passenger_id)

    @staticmethod
    def get_by_booking(
        session: Session,
        booking_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Passenger]:
        statement = select(Passenger).where(Passenger.booking_id == booking_id)
        statement = statement.offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Passenger]:
        statement = select(Passenger).offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def update(
        session: Session,
        passenger_id: UUID,
        **kwargs,
    ) -> Optional[Passenger]:
        p = session.get(Passenger, passenger_id)
        if not p:
            return None
        for k, v in kwargs.items():
            if hasattr(p, k) and v is not None:
                setattr(p, k, v)
        session.add(p)
        session.commit()
        session.refresh(p)
        return p

    @staticmethod
    def delete(session: Session, passenger_id: UUID) -> bool:
        p = session.get(Passenger, passenger_id)
        if not p:
            return False
        session.delete(p)
        session.commit()
        return True

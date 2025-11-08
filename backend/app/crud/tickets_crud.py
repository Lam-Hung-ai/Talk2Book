from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.tickets import Ticket


class TicketsCRUD:
    """CRUD operations for Ticket"""

    @staticmethod
    def create(
        session: Session,
        code: str,
        booking_item_id: Optional[UUID] = None,
        issued_at: Optional[datetime] = None,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        status: Optional[str] = None,
        data: Optional[dict] = None,
    ) -> Ticket:
        t = Ticket(
            code=code,
            booking_item_id=booking_item_id,
            issued_at=issued_at or datetime.utcnow(),
            valid_from=valid_from,
            valid_to=valid_to,
            status=status,
            data=data,
        )
        session.add(t)
        session.commit()
        session.refresh(t)
        return t

    @staticmethod
    def get_by_id(session: Session, ticket_id: UUID) -> Optional[Ticket]:
        return session.get(Ticket, ticket_id)

    @staticmethod
    def get_by_booking_item(
        session: Session,
        booking_item_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Ticket]:
        statement = select(Ticket).where(Ticket.booking_item_id == booking_item_id)
        statement = statement.offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Ticket]:
        statement = select(Ticket).offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def update(
        session: Session,
        ticket_id: UUID,
        **kwargs,
    ) -> Optional[Ticket]:
        t = session.get(Ticket, ticket_id)
        if not t:
            return None
        for k, v in kwargs.items():
            if hasattr(t, k) and v is not None:
                setattr(t, k, v)
        session.add(t)
        session.commit()
        session.refresh(t)
        return t

    @staticmethod
    def delete(session: Session, ticket_id: UUID) -> bool:
        t = session.get(Ticket, ticket_id)
        if not t:
            return False
        session.delete(t)
        session.commit()
        return True

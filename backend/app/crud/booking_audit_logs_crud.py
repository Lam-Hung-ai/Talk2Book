from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.booking_audit_logs import BookingAuditLog


class BookingAuditLogCRUD:
    """CRUD operations for BookingAuditLog"""

    @staticmethod
    def create(
        session: Session,
        booking_id: UUID,
        action: str,
        actor_type: str = "system",
        actor_id: Optional[UUID] = None,
        from_state: Optional[str] = None,
        to_state: Optional[str] = None,
        meta: Optional[dict] = None,
    ) -> BookingAuditLog:
        """Tạo một entry audit mới cho booking"""
        entry = BookingAuditLog(
            booking_id=booking_id,
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            from_state=from_state,
            to_state=to_state,
            meta=meta,
            created_at=datetime.utcnow(),
        )
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return entry

    @staticmethod
    def get_by_id(session: Session, entry_id: UUID) -> Optional[BookingAuditLog]:
        """Lấy audit entry theo ID"""
        return session.get(BookingAuditLog, entry_id)

    @staticmethod
    def get_by_booking(
        session: Session,
        booking_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[BookingAuditLog]:
        """Lấy các audit entries cho một booking"""
        statement = select(BookingAuditLog).where(BookingAuditLog.booking_id == booking_id)
        statement = statement.offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def get_by_actor(
        session: Session,
        actor_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[BookingAuditLog]:
        """Lấy audit entries theo actor_id"""
        statement = select(BookingAuditLog).where(BookingAuditLog.actor_id == actor_id)
        statement = statement.offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def get_all(
        session: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> List[BookingAuditLog]:
        """Lấy tất cả audit entries"""
        statement = select(BookingAuditLog).offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def update(
        session: Session,
        entry_id: UUID,
        action: Optional[str] = None,
        from_state: Optional[str] = None,
        to_state: Optional[str] = None,
        meta: Optional[dict] = None,
    ) -> Optional[BookingAuditLog]:
        """Cập nhật một audit entry (thường không cần thiết nhưng có sẵn)"""
        entry = session.get(BookingAuditLog, entry_id)
        if not entry:
            return None

        if action is not None:
            entry.action = action
        if from_state is not None:
            entry.from_state = from_state
        if to_state is not None:
            entry.to_state = to_state
        if meta is not None:
            entry.meta = meta

        session.add(entry)
        session.commit()
        session.refresh(entry)
        return entry

    @staticmethod
    def delete(session: Session, entry_id: UUID) -> bool:
        """Xóa audit entry"""
        entry = session.get(BookingAuditLog, entry_id)
        if not entry:
            return False

        session.delete(entry)
        session.commit()
        return True

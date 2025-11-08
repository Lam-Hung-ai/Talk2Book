from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.price_quotes import PriceQuote


class PriceQuoteCRUD:
    """CRUD operations for PriceQuote"""

    @staticmethod
    def create(
        session: Session,
        user_id: Optional[UUID],
        currency_code: str,
        total_amount: float,
        quote_data: Optional[dict] = None,
        expires_at: Optional[datetime] = None,
        integrity_token: Optional[str] = None,
    ) -> PriceQuote:
        pq = PriceQuote(
            user_id=user_id,
            currency_code=currency_code,
            total_amount=total_amount,
            quote_data=quote_data,
            expires_at=expires_at,
            integrity_token=integrity_token,
            created_at=datetime.utcnow(),
        )
        session.add(pq)
        session.commit()
        session.refresh(pq)
        return pq

    @staticmethod
    def get_by_id(session: Session, pq_id: UUID) -> Optional[PriceQuote]:
        return session.get(PriceQuote, pq_id)

    @staticmethod
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[PriceQuote]:
        statement = select(PriceQuote).offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def update(session: Session, pq_id: UUID, **kwargs) -> Optional[PriceQuote]:
        pq = session.get(PriceQuote, pq_id)
        if not pq:
            return None
        for k, v in kwargs.items():
            if hasattr(pq, k) and v is not None:
                setattr(pq, k, v)
        session.add(pq)
        session.commit()
        session.refresh(pq)
        return pq

    @staticmethod
    def delete(session: Session, pq_id: UUID) -> bool:
        pq = session.get(PriceQuote, pq_id)
        if not pq:
            return False
        session.delete(pq)
        session.commit()
        return True

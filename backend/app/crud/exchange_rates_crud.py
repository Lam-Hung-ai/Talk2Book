from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.models.exchange_rates import ExchangeRate


class ExchangeRatesCRUD:
    """CRUD operations for ExchangeRate"""

    @staticmethod
    def create(
        session: Session,
        rate_date: date,
        base_currency: str,
        target_currency: str,
        rate: float,
    ) -> ExchangeRate:
        ex = ExchangeRate(
            rate_date=rate_date,
            base_currency=base_currency,
            target_currency=target_currency,
            rate=rate,
        )
        session.add(ex)
        session.commit()
        session.refresh(ex)
        return ex

    @staticmethod
    def get_by_id(session: Session, ex_id: UUID) -> Optional[ExchangeRate]:
        return session.get(ExchangeRate, ex_id)

    @staticmethod
    def get_by_date_pair(
        session: Session,
        rate_date: date,
        base_currency: str,
        target_currency: str,
    ) -> Optional[ExchangeRate]:
        statement = select(ExchangeRate).where(
            (ExchangeRate.rate_date == rate_date)
            & (ExchangeRate.base_currency == base_currency)
            & (ExchangeRate.target_currency == target_currency)
        )
        return session.exec(statement).first()

    @staticmethod
    def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[ExchangeRate]:
        statement = select(ExchangeRate).offset(skip).limit(limit)
        return list(session.exec(statement).all())

    @staticmethod
    def update(
        session: Session,
        ex_id: UUID,
        rate: Optional[float] = None,
    ) -> Optional[ExchangeRate]:
        ex = session.get(ExchangeRate, ex_id)
        if not ex:
            return None
        if rate is not None:
            ex.rate = rate
        session.add(ex)
        session.commit()
        session.refresh(ex)
        return ex

    @staticmethod
    def delete(session: Session, ex_id: UUID) -> bool:
        ex = session.get(ExchangeRate, ex_id)
        if not ex:
            return False
        session.delete(ex)
        session.commit()
        return True

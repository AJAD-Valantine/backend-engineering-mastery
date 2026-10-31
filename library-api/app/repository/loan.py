from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.book_copy import BookCopy
from app.models.loan import Loan


class LoanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, loan: Loan) -> Loan:
        self.db.add(loan)
        self.db.flush()
        self.db.refresh(loan)
        return loan

    def read_by_id(self, pk: int) -> Loan | None:
        stmt = (
            select(Loan)
            .options(
                joinedload(Loan.book_copy).joinedload(BookCopy.book),
                joinedload(Loan.user),
            )
            .where(Loan.loan_id == pk)
        )
        return self.db.scalar(stmt)

    def read_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> list[Loan]:
        stmt = (
            select(Loan)
            .options(
                joinedload(Loan.book_copy).joinedload(BookCopy.book),
                joinedload(Loan.user),
            )
        )
        if active_only:
            stmt = stmt.where(Loan.returned_at.is_(None))
        stmt = stmt.order_by(Loan.borrowed_at.desc()).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def read_by_user_id(
        self,
        user_id: UUID,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Loan]:
        stmt = (
            select(Loan)
            .options(
                joinedload(Loan.book_copy).joinedload(BookCopy.book),
                joinedload(Loan.user),
            )
            .where(Loan.user_id == user_id)
        )
        if active_only:
            stmt = stmt.where(Loan.returned_at.is_(None))
        stmt = stmt.order_by(Loan.borrowed_at.desc()).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def read_by_copy_id(
        self,
        copy_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Loan]:
        stmt = (
            select(Loan)
            .options(
                joinedload(Loan.book_copy).joinedload(BookCopy.book),
                joinedload(Loan.user),
            )
            .where(Loan.book_copy_id == copy_id)
            .order_by(Loan.borrowed_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def read_active_loan_by_copy_id(self, copy_id: int) -> Loan | None:
        stmt = select(Loan).where(
            Loan.book_copy_id == copy_id,
            Loan.returned_at.is_(None),
        )
        return self.db.scalar(stmt)

    def count(self, active_only: bool = False) -> int:
        stmt = select(func.count(Loan.loan_id))
        if active_only:
            stmt = stmt.where(Loan.returned_at.is_(None))
        return self.db.scalar(stmt) or 0

    def update(self, loan: Loan, new_data: dict[str, Any] | None = None) -> Loan:
        if new_data:
            for k, v in new_data.items():
                setattr(loan, k, v)
        self.db.flush()
        self.db.refresh(loan)
        return loan

    def mark_as_returned(
        self,
        loan: Loan,
        returned_at: datetime | None = None,
    ) -> Loan:
        loan.returned_at = returned_at or datetime.now(UTC)
        self.db.flush()
        self.db.refresh(loan)
        return loan

    def delete(self, loan: Loan) -> None:
        self.db.delete(loan)
        self.db.flush()

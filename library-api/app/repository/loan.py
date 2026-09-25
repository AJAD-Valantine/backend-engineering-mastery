from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.loan import Loan


class LoanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, book: Loan) -> Loan:

        self.db.add(book)
        self.db.flush()
        self.db.refresh(book)

        return book

    def read_by_id(self, pk: int) -> Loan | None:

        return self.db.get(Loan, pk)

    def update(self, loan: Loan) -> Loan:

        loan.returned_at = datetime.now(UTC)

        self.db.flush()
        self.db.refresh(loan)

        return loan

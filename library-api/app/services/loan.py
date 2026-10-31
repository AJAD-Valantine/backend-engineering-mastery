from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status

from app.models.book_copy import CopyStatus
from app.models.loan import Loan
from app.repository.book import BookRepository
from app.repository.loan import LoanRepository
from app.repository.user import UserRepository
from app.schemas.loan import (
    LoanBorrowRequest,
    LoanCreateRequest,
    LoanReturnRequest,
    LoanUpdateRequest,
)


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


class LoanService:
    def __init__(
        self,
        loan_repository: LoanRepository,
        book_repository: BookRepository,
        user_repository: UserRepository,
    ) -> None:
        self.loan_repository = loan_repository
        self.book_repository = book_repository
        self.user_repository = user_repository

    def create_loan(self, request: LoanCreateRequest) -> Loan:
        return self._create_loan_internal(
            user_id=request.user_id,
            book_copy_id=request.book_copy_id,
            due_at=request.due_at,
        )

    def borrow_book(self, user_id: UUID, request: LoanBorrowRequest) -> Loan:
        return self._create_loan_internal(
            user_id=user_id,
            book_copy_id=request.book_copy_id,
            due_at=request.due_at,
        )

    def _create_loan_internal(
        self,
        user_id: UUID,
        book_copy_id: int,
        due_at: datetime | None = None,
    ) -> Loan:
        # 1. Validate user
        user = self.user_repository.read_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
        if not user.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is inactive and cannot borrow books",
            )

        # 2. Validate book copy
        copy = self.book_repository.read_copy_by_id(book_copy_id)
        if copy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book copy with ID {book_copy_id} not found",
            )
        if copy.status != CopyStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book copy is not available for loan (status: '{copy.status.value}')",
            )

        # 3. Check if copy is already actively borrowed
        active_loan = self.loan_repository.read_active_loan_by_copy_id(book_copy_id)
        if active_loan is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book copy with ID {book_copy_id} is currently loaned out",
            )

        # 4. Determine dates
        now = datetime.now(UTC)
        final_due_at = due_at if due_at is not None else (now + timedelta(days=14))

        if _to_utc(final_due_at) <= _to_utc(now):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Due date must be after the borrowed date",
            )

        new_loan = Loan(
            book_copy_id=book_copy_id,
            user_id=user_id,
            borrowed_at=now,
            due_at=final_due_at,
            returned_at=None,
        )

        created_loan = self.loan_repository.create(new_loan)
        loan_with_relations = self.loan_repository.read_by_id(created_loan.loan_id)
        return loan_with_relations or created_loan

    def return_book(
        self,
        loan_id: int,
        request: LoanReturnRequest | None = None,
    ) -> Loan:
        loan = self.get_loan_by_id(loan_id)

        if loan.returned_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This book copy has already been returned",
            )

        returned_at = (
            request.returned_at
            if (request and request.returned_at is not None)
            else datetime.now(UTC)
        )

        if _to_utc(returned_at) < _to_utc(loan.borrowed_at):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Return date cannot be earlier than borrowed date",
            )

        updated_loan = self.loan_repository.mark_as_returned(loan, returned_at)
        refreshed = self.loan_repository.read_by_id(updated_loan.loan_id)
        return refreshed or updated_loan

    def get_loan_by_id(self, loan_id: int) -> Loan:
        loan = self.loan_repository.read_by_id(loan_id)
        if loan is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Loan with ID {loan_id} not found",
            )
        return loan

    def get_all_loans(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> list[Loan]:
        return self.loan_repository.read_all(
            skip=skip, limit=limit, active_only=active_only
        )

    def get_user_loans(
        self,
        user_id: UUID,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Loan]:
        user = self.user_repository.read_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
        return self.loan_repository.read_by_user_id(
            user_id=user_id,
            active_only=active_only,
            skip=skip,
            limit=limit,
        )

    def get_copy_loans(
        self,
        copy_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Loan]:
        copy = self.book_repository.read_copy_by_id(copy_id)
        if copy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book copy with ID {copy_id} not found",
            )
        return self.loan_repository.read_by_copy_id(
            copy_id=copy_id, skip=skip, limit=limit
        )

    def update_loan(self, loan_id: int, loan_data: LoanUpdateRequest) -> Loan:
        loan = self.get_loan_by_id(loan_id)
        update_dict = loan_data.model_dump(exclude_unset=True)

        loan_borrowed = _to_utc(loan.borrowed_at)

        if "due_at" in update_dict and update_dict["due_at"] is not None:
            comp_due = _to_utc(update_dict["due_at"])
            if comp_due <= loan_borrowed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Due date must be after borrowed date",
                )

        if "returned_at" in update_dict and update_dict["returned_at"] is not None:
            comp_returned = _to_utc(update_dict["returned_at"])
            if comp_returned < loan_borrowed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Return date cannot be earlier than borrowed date",
                )

        if not update_dict:
            return loan

        self.loan_repository.update(loan, update_dict)
        refreshed = self.loan_repository.read_by_id(loan_id)
        return refreshed or loan

    def delete_loan(self, loan_id: int) -> None:
        loan = self.get_loan_by_id(loan_id)
        self.loan_repository.delete(loan)

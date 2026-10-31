from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.base import AppBaseModel
from app.schemas.book_copy import BookCopyResponse
from app.schemas.user import UserResponse


class LoanCreateRequest(AppBaseModel):
    book_copy_id: int = Field(..., gt=0)
    user_id: UUID
    due_at: datetime | None = None


class LoanBorrowRequest(AppBaseModel):
    book_copy_id: int = Field(..., gt=0)
    due_at: datetime | None = None


class LoanReturnRequest(AppBaseModel):
    returned_at: datetime | None = None


class LoanUpdateRequest(AppBaseModel):
    due_at: datetime | None = None
    returned_at: datetime | None = None


class LoanResponse(AppBaseModel):
    loan_id: int
    book_copy: BookCopyResponse
    user: UserResponse
    borrowed_at: datetime
    due_at: datetime
    returned_at: datetime | None = None

from datetime import datetime

from pydantic import Field

from app.schemas.base import AppBaseModel
from app.schemas.book_copy import BookCopyResponse
from app.schemas.user import UserResponse


class LoanBorrowRequest(AppBaseModel):

    book_copy_id: int = Field(..., gt=0)

class LoanReturnRequest(AppBaseModel):

    returned_at: datetime = Field(...)

class LoanResponse(AppBaseModel):
    loan_id: int
    book_copy: BookCopyResponse
    user: UserResponse
    borrowed_at: datetime
    due_at: datetime
    returned_at: datetime | None

from pydantic import Field

from app.models.book_copy import CopyStatus
from app.schemas.base import AppBaseModel
from app.schemas.book import BookResponse


class BookCopyCreateRequest(AppBaseModel):
    book_id: int = Field(..., gt=0)
    status: CopyStatus = CopyStatus.ACTIVE


class BookCopyUpdateRequest(AppBaseModel):
    status: CopyStatus


class BookCopyResponse(AppBaseModel):
    book_copy_id: int
    book: BookResponse
    status: CopyStatus

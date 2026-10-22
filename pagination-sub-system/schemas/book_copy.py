from models.book_copy import CopyStatus

from schemas.base import AppBaseModel


class BookCopyResponse(AppBaseModel):
    book_copy_id: int
    status: CopyStatus

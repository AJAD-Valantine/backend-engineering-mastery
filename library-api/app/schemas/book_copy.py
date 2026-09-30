from app.schemas.base import AppBaseModel
from app.schemas.book import BookResponse


class BookCopyResponse(AppBaseModel):

    book_copy_id: int
    book: BookResponse
    status: str

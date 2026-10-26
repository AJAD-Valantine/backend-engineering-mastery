from datetime import date, datetime

from core.config import get_settings
from core.enums import CopyStatus
from pydantic import Field

from schemas.author import AuthorResponse
from schemas.base import AppBaseModel
from schemas.book_copy import BookCopyResponse
from schemas.category import CategoryResponse

settings = get_settings()

class BookFilter(AppBaseModel):
    publish_date_before: datetime | None = None
    publish_date_after: datetime | None = None
    page_count_max: int | None = None
    page_count_min: int | None = None
    language: list[str] | None = None
    category: list[str] | None = None
    author: list[str] | None = None
    status: list[CopyStatus] | None = None

class BookSort(AppBaseModel):
    sort: str  = settings.DEFAULT_SORT

class BookSearch(AppBaseModel):
    q: str | None = None

class OffsetLimitPagination(AppBaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)

class PageNumberPageSizePagination(AppBaseModel):
    page_number: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class BookResponse(AppBaseModel):
    book_id: int
    title: str
    publish_date: date
    page_count: int
    language: str
    description: str
    authors: list[AuthorResponse]
    categories: list[CategoryResponse]
    copies: list[BookCopyResponse]


class OffsetLimitBookResponse(AppBaseModel):
    data: list[BookResponse]
    total: int
    offset: int
    limit: int
    has_next: bool
    has_prev: bool


class PageNumPageSizeBookResponse(AppBaseModel):
    data: list[BookResponse]
    total: int
    page_number: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

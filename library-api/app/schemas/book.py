from datetime import date, datetime

from pydantic import Field

from app.schemas.base import AppBaseModel


class BookCreateRequest(AppBaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    isbn: str = Field(..., min_length=13, max_length=17)
    publish_date: date = Field(...)
    page_count: int = Field(..., gt=0)
    language: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=10, max_length=2000)


class BookUpdateRequest(AppBaseModel):
    title: str | None = Field(None, min_length=2, max_length=200)
    isbn: str | None = Field(None, min_length=13, max_length=17)
    publish_date: date | None = Field(None)
    page_count: int | None = Field(None, gt=0)
    language: str | None = Field(None, min_length=2, max_length=50)
    description: str | None = Field(None, min_length=10, max_length=2000)


class BookResponse(AppBaseModel):
    book_id: int
    title: str
    isbn: str
    publish_date: date
    page_count: int
    language: str
    description: str
    updated_at: datetime

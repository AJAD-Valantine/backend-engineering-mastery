from datetime import date, datetime

from pydantic import Field, field_validator

from app.schemas.base import AppBaseModel


class BookCreateRequest(AppBaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    isbn: str = Field(..., min_length=10, max_length=17)
    publish_date: date = Field(...)
    page_count: int = Field(..., gt=0)
    language: str = Field(..., min_length=2, max_length=15)
    description: str = Field(..., min_length=10, max_length=2000)

    @field_validator("isbn", mode="after")
    @classmethod
    def clean_isbn(cls, v: str) -> str:
        clean: str = v.replace("-", "").replace(" ", "").strip()
        if len(clean) not in (10, 13):
            raise ValueError("ISBN must be 10 or 13 characters long")
        return clean


class BookUpdateRequest(AppBaseModel):
    title: str | None = Field(None, min_length=2, max_length=100)
    isbn: str | None = Field(None, min_length=10, max_length=17)
    publish_date: date | None = Field(None)
    page_count: int | None = Field(None, gt=0)
    language: str | None = Field(None, min_length=2, max_length=15)
    description: str | None = Field(None, min_length=10, max_length=2000)

    @field_validator("isbn", mode="after")
    @classmethod
    def clean_isbn(cls, v: str | None) -> str | None:
        if v is None:
            return None
        clean: str = v.replace("-", "").replace(" ", "").strip()
        if len(clean) not in (10, 13):
            raise ValueError("ISBN must be 10 or 13 characters long")
        return clean


class BookResponse(AppBaseModel):
    book_id: int
    title: str
    isbn: str
    publish_date: date
    page_count: int
    language: str
    description: str
    updated_at: datetime

from collections.abc import Generator
from datetime import datetime
from typing import Annotated, Any

from core.config import get_settings
from core.database import SessionLocal
from core.enums import CopyStatus
from fastapi import Depends
from fastapi.params import Query
from repository import BookRepository
from schemas.book import (
    BookFilter,
    BookSearch,
    BookSort,
    OffsetLimitPagination,
    PageNumberPageSizePagination,
)
from service import BookService
from sqlalchemy.orm import Session

settings = get_settings()


def filter(
    publish_date_before: datetime | None = None,
    publish_date_after: datetime | None = None,
    page_count_max: int | None = None,
    page_count_min: int | None = None,
    language: Annotated[list[str] | None, Query()] = None,
    category: Annotated[list[str] | None, Query()] = None,
    author: Annotated[list[str] | None, Query()] = None,
    status: Annotated[list[CopyStatus] | None, Query()] = None,
) -> BookFilter:

    return BookFilter(
        page_count_max=page_count_max,
        page_count_min=page_count_min,
        publish_date_after=publish_date_after,
        publish_date_before=publish_date_before,
        language=language,
        category=category,
        author=author,
        status=status,
    )


BookFilterDep = Annotated[BookFilter, Depends(filter)]


def sort(
    sort: Annotated[str, Query()] = settings.DEFAULT_SORT,
) -> BookSort:

    return BookSort(
        sort=sort,
    )


BookSortDep = Annotated[BookSort, Depends(sort)]


def search(q: Annotated[str | None, Query()] = None) -> BookSearch:

    return BookSearch(q=q)


BookSearchDep = Annotated[BookSearch, Depends(search)]


def offset_limit(
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 20,
) -> OffsetLimitPagination:

    return OffsetLimitPagination(
        offset=offset,
        limit=limit,
    )


OffsetLimitDep = Annotated[OffsetLimitPagination, Depends(offset_limit)]


def page_number_page_size(
    page_number: Annotated[int, Query()] = 1,
    page_size: Annotated[int, Query()] = 20,
) -> PageNumberPageSizePagination:

    return PageNumberPageSizePagination(
        page_number=page_number,
        page_size=page_size,
    )


PageNumberPageSizeDep = Annotated[
    PageNumberPageSizePagination, Depends(page_number_page_size)
]


def get_db() -> Generator[Session, Any, None]:
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]


def get_book_repo(db: SessionDep) -> BookRepository:
    return BookRepository(db)


BookRepoDep = Annotated[BookRepository, Depends(get_book_repo)]


def get_book_service(book_repo: BookRepoDep) -> BookService:
    return BookService(book_repo)


BookServiceDep = Annotated[BookService, Depends(get_book_service)]

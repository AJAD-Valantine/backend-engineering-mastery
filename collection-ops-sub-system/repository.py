from collections.abc import Sequence

from core.config import get_settings
from fastapi import HTTPException
from models.author import Author
from models.book import Book
from models.book_copy import BookCopy
from models.category import Category
from schemas.book import BookFilter, BookSort
from sqlalchemy import func, nulls_last, or_, select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.orm.query import Query

BOOK_SORTABLE_FIELDS = {
    "page_count": Book.page_count,
    "publish_date": Book.publish_date,
    "book_id": Book.book_id,
}


class BookRepository:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def get_base_query(self) -> Query[Book]:
        return self.db.query(Book)

    def apply_book_filtering(
        self, base_query: Query[Book], filters: BookFilter
    ) -> Query[Book]:
        query = base_query

        if filters.publish_date_before is not None:
            query = query.filter(Book.publish_date < filters.publish_date_before)

        if filters.publish_date_after is not None:
            query = query.filter(Book.publish_date > filters.publish_date_after)

        if filters.page_count_max is not None:
            query = query.filter(Book.page_count < filters.page_count_max)

        if filters.page_count_min is not None:
            query = query.filter(Book.page_count > filters.page_count_min)

        if filters.language:
            query = query.filter(Book.language.in_(filters.language))

        if filters.category:
            query = query.filter(
                Book.categories.any(Category.name.in_(filters.category))
            )

        if filters.author:
            full_name = func.concat(Author.first_name, " ", Author.last_name)
            query = query.filter(Book.authors.any(full_name.in_(filters.author)))

        if filters.status:
            query = query.filter(Book.copies.any(BookCopy.status.in_(filters.status)))

        query = query.options(
            selectinload(Book.authors),
            selectinload(Book.categories),
            selectinload(Book.copies),
        )

        return query

    def apply_book_sorting(
        self, sort_params: BookSort, filterd_query: Query[Book]
    ) -> Query[Book]:

        list_of_params: list[str] = [
            param.strip()
            for param in sort_params.sort.strip().split(",")
            if param.strip()
        ]

        if len(list_of_params) > self.settings.MAX_SORT_FIELDS:
            raise HTTPException(
                status_code=400,
                detail=f"Too many sort fields. Maximum is {self.settings.MAX_SORT_FIELDS}.",
            )

        order_clauses = []
        fields = []

        for param in list_of_params:
            if param.strip().startswith("-"):
                field_name: str = param[1:]
                direction: str = "desc"
            else:
                field_name: str = param
                direction: str = "asc"

            if field_name in fields:
                raise HTTPException(
                    status_code=400,
                    detail=f"Duplicate sort fields. {field_name}.",
                )

            fields.append(field_name)

            column_name = BOOK_SORTABLE_FIELDS.get(field_name)

            if column_name is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid sort field '{field_name}'.",
                )

            if direction == "desc":
                order_clauses.append(nulls_last(column_name.desc()))
            else:
                order_clauses.append(nulls_last(column_name.asc()))

        return filterd_query.order_by(*order_clauses).options(
            selectinload(Book.authors),
            selectinload(Book.categories),
            selectinload(Book.copies),
        )

    def execute_query(self, query: Query[Book]):
        return self.db.scalars(query).all()

    def get_books_with_simple_pagination(
        self, offset: int = 0, limit: int = 20
    ) -> Sequence[Book]:
        stmt = select(Book).offset(offset).limit(limit)
        return self.db.scalars(stmt).all()

    def count_books(self) -> int:
        stmt = select(func.count(Book.book_id))
        return self.db.scalar(stmt) or 0

    def search_book_with_patterns(self, search_term: str):

        stmt = (
            select(Book)
            .filter(
                or_(Book.title.ilike(search_term), Book.description.ilike(search_term))
            )
            .options(
                selectinload(Book.authors),
                selectinload(Book.categories),
                selectinload(Book.copies),
            )
        )

        return self.db.scalars(stmt).all()

    def search_books_with_vectors(self, search_term: str):

        search_query = func.plainto_tsquery("english", search_term)

        rank = func.ts_rank(
            Book.search_vector,
            search_query,
        ).label("rank")

        stmt = (
            select(Book)
            .where(Book.search_vector.op("@@")(search_query))
            .order_by(rank.desc(), Book.book_id.asc())
        ).options(
            selectinload(Book.authors),
            selectinload(Book.categories),
            selectinload(Book.copies),
        )

        return self.db.scalars(stmt).all()

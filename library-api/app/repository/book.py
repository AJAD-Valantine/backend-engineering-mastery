from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.book import Book
from app.models.book_copy import BookCopy


class BookRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, book: Book) -> Book:
        self.db.add(book)
        self.db.flush()
        self.db.refresh(book)
        return book

    def read_by_id(self, pk: int) -> Book | None:
        return self.db.get(Book, pk)

    def read_by_isbn(self, isbn: str) -> Book | None:
        stmt = select(Book).where(Book.isbn == isbn)
        return self.db.scalar(stmt)

    def read_all(self) -> list[Book]:
        stmt = select(Book)
        return list(self.db.scalars(stmt).all())

    def update(self, book: Book, new_data: dict[str, Any]) -> Book:
        for k, v in new_data.items():
            setattr(book, k, v)
        self.db.flush()
        self.db.refresh(book)
        return book

    def delete(self, book: Book) -> None:
        self.db.delete(book)
        self.db.flush()

    # -- Book Copy Operations -- #

    def create_copy(self, copy: BookCopy) -> BookCopy:
        self.db.add(copy)
        self.db.flush()
        self.db.refresh(copy)
        return copy

    def read_copy_by_id(self, copy_id: int) -> BookCopy | None:
        stmt = (
            select(BookCopy)
            .options(joinedload(BookCopy.book))
            .where(BookCopy.book_copy_id == copy_id)
        )
        return self.db.scalar(stmt)

    def read_copies_by_book_id(self, book_id: int) -> list[BookCopy]:
        stmt = (
            select(BookCopy)
            .options(joinedload(BookCopy.book))
            .where(BookCopy.book_id == book_id)
            .order_by(BookCopy.book_copy_id.asc())
        )
        return list(self.db.scalars(stmt).all())

    def update_copy(self, copy: BookCopy, new_data: dict[str, Any]) -> BookCopy:
        for k, v in new_data.items():
            setattr(copy, k, v)
        self.db.flush()
        self.db.refresh(copy)
        return copy

    def delete_copy(self, copy: BookCopy) -> None:
        self.db.delete(copy)
        self.db.flush()

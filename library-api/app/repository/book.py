from typing import Any

from sqlalchemy.orm import Session

from app.models.book import Book


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

    def update(self, book: Book, new_data: dict[str, Any]) -> Book:

        for k, v in new_data.items():
            setattr(book, k, v)

        self.db.flush()
        self.db.refresh(book)

        return book

    def delete(self, book: Book) -> None:

        self.db.delete(book)
        self.db.flush()

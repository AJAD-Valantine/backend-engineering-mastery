from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.author import Author


class AuthorRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, author: Author) -> Author:
        self.db.add(author)
        self.db.refresh(author)
        self.db.flush()
        return author

    def read_by_email(self, email: str) -> Author | None:
        stmt = select(Author).where(Author.email == email)

        return self.db.scalar(stmt)

    def read_by_id(self, author_id: int) -> Author | None:
        stmt = select(Author).where(Author.author_id == author_id)

        return self.db.scalar(stmt)

    def read_all(self) -> Sequence[Author]:
        stmt = select(Author)
        return self.db.scalars(stmt).all()

    def update(self, author: Author, new_data: dict[str, Any]) -> Author:
        for k, v in new_data.items():
            setattr(author, k, v)
        self.db.flush()
        self.db.refresh(author)
        return author

    def delete(self, author: Author) -> None:
        self.db.delete(author)
        self.db.flush()

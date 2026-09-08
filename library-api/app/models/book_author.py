from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BookAuthor(Base):
    __tablename__ = "book_authors"

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.book_id"),
        primary_key=True
        )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("authors.author_id"),
        primary_key=True
    )

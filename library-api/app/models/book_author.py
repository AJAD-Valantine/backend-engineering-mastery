from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BookAuthor(Base):
    __tablename__ = "book_authors"

    # -- COLUMNS -- #

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.book_id", ondelete="CASCADE")
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("authors.author_id", ondelete="CASCADE")
    )

    # -- TABLE ARGS -- #

    __table_args__ = PrimaryKeyConstraint(
        "book_id", "author_id", name="pk_book_authors"
    )

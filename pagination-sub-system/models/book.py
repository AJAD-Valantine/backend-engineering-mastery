from datetime import date, datetime

from core.database import Base
from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Book(Base):
    __tablename__ = "books"

    # -- COLUMNS -- #

    book_id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(100), nullable=False)

    isbn: Mapped[str] = mapped_column(String(13), unique=True, nullable=False)

    publish_date: Mapped[date] = mapped_column(Date, nullable=False)

    page_count: Mapped[int] = mapped_column(nullable=False)

    language: Mapped[str] = mapped_column(String(15), nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    search_vector: Mapped[str] = mapped_column(TSVECTOR, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=False,
        server_default=func.now(),
    )

    # -- RELATIONSHIPS -- #

    authors: Mapped[list["Author"]] = relationship(  # type: ignore  # noqa: F821
        secondary="book_authors", back_populates="books"
    )

    categories: Mapped[list["Category"]] = relationship(  # type: ignore  # noqa: F821
        secondary="book_categories", back_populates="books"
    )

    copies: Mapped[list["BookCopy"]] = relationship(  # type: ignore  # noqa: F821
        back_populates="book", cascade="all, delete-orphan"
    )

    # -- TABLE ARGS -- #

    __table_args__ = (
        # Indexes
        Index("ix_books_title", "title"),
        Index("ix_books_language", "language"),
        Index("ix_books_publish_date", "publish_date"),
        Index("ix_books_publish_date_id", "publish_date", "book_id"),
        Index("ix_books_page_count_id", "page_count", "book_id"),
        Index("ix_books_search_vector", "search_vector", postgresql_using="gin"),
        # Constraints
        CheckConstraint("page_count > 0", name="page_count_positive"),
        CheckConstraint(
            "char_length(isbn) = 10 OR char_length(isbn) = 13", name="isbn_length"
        ),
        CheckConstraint("publish_date <= CURRENT_DATE", name="publish_date_not_future"),
    )

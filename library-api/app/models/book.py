from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Book(Base):
    __tablename__ = "books"

    book_id: Mapped[int] = mapped_column(
        primary_key=True
        )

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False
        )

    publish_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
        )

    page_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False
        )

    language: Mapped[str] = mapped_column(
        String(15),
        nullable=False
        )

    description: Mapped[str] = mapped_column(
        String(250),
        nullable=False
        )

    authors: Mapped[list["Author"]] = relationship(  # type: ignore  # noqa: F821
        secondary="book_authors", back_populates="books"
    )

    categories: Mapped[list["Category"]] = relationship(  # type: ignore  # noqa: F821
        secondary="book_categories",
        back_populates="books"
    )

    copies: Mapped[list["BookCopy"]] = relationship(  # type: ignore  # noqa: F821
        back_populates="book"
    )

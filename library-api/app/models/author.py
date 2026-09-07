from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Author(Base):
    __tablename__ = "authors"

    author_id: Mapped[int] = mapped_column(
        primary_key=True
        )

    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
        )

    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
        )

    books: Mapped[list["Book"]] = relationship(  # type: ignore  # noqa: F821
        secondary="book_authors", back_populates="authors"
    )

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Author(Base):
    __tablename__ = "authors"

    # -- COLUMNS -- #

    author_id: Mapped[int] = mapped_column(primary_key=True)

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)

    last_name: Mapped[str] = mapped_column(String(50), nullable=False)

    # -- RELATIONSHIPS -- #

    books: Mapped[list["Book"]] = relationship(  # type: ignore  # noqa: F821
        secondary="book_authors", back_populates="authors"
    )

    # -- TABLE ARGS -- #

    __table_args__ = (
        CheckConstraint("char_length(first_name) >= 2", name="first_name_min"),
        CheckConstraint("char_length(last_name) >= 2", name="last_name_min"),
    )

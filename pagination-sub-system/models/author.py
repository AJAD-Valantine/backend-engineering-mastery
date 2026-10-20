from datetime import datetime

from core.database import Base
from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Author(Base):
    __tablename__ = "authors"

    # -- COLUMNS -- #

    author_id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)

    last_name: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # -- RELATIONSHIPS -- #

    books: Mapped[list["Book"]] = relationship(  # type: ignore  # noqa: F821
        secondary="book_authors", back_populates="authors"
    )

    # -- TABLE ARGS -- #

    __table_args__ = (
        CheckConstraint("char_length(first_name) >= 2", name="first_name_min"),
        CheckConstraint("char_length(last_name) >= 2", name="last_name_min"),
    )

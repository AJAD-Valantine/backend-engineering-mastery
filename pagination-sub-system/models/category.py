from datetime import datetime

from core.database import Base
from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Category(Base):
    __tablename__ = "categories"

    # -- COLUMNS -- #

    category_id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(25),
        nullable=False,
        unique=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # -- RELATIONSHIPS -- #

    books: Mapped[list["Book"]] = relationship(  # type: ignore  # noqa: F821
        secondary="book_categories", back_populates="categories"
    )

    # -- TABLE ARGS -- #

    __table_args__ = (
        CheckConstraint("char_length(name) >= 2", name="category_name_min"),
    )

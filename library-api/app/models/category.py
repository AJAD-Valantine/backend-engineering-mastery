from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    # -- COLUMNS -- #

    category_id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(25),
        nullable=False,
        unique=True,
    )

    # -- RELATIONSHIPS -- #

    books: Mapped[list["Book"]] = relationship(  # type: ignore  # noqa: F821
        secondary="book_categories", back_populates="categories"
    )

    # -- TABLE ARGS -- #

    __table_args__ = (
        CheckConstraint("char_length(name) >= 2", name="category_name_min"),
    )

from core.database import Base
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column


class BookCategory(Base):
    __tablename__ = "book_categories"

    # -- COLUMNS -- #

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.book_id", ondelete="CASCADE")
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.category_id", ondelete="CASCADE")
    )

    # -- TABLE ARGS -- #

    __table_args__ = (
        PrimaryKeyConstraint("book_id", "category_id", name="pk_book_categories"),
    )

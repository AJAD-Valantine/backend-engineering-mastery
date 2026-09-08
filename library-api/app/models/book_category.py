from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BookCategory(Base):
    __tablename__ = "book_categories"

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.book_id"),
        primary_key=True
        )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.category_id"),
        primary_key=True
    )

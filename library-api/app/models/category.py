from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    category_id: Mapped[int] = mapped_column(
        primary_key=True
        )

    name: Mapped[str] = mapped_column(
        String(25),
        nullable=False
        )

    books: Mapped[list["Book"]] = relationship(  # type: ignore  # noqa: F821
        secondary="book_categories", back_populates="categories"
    )

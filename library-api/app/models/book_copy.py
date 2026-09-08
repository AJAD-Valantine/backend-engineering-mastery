from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BookCopy(Base):
    __tablename__ = "book_copies"

    book_copy_id: Mapped[int] = mapped_column(
        primary_key=True
    )

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.book_id")
        )

    is_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True
        )

    book: Mapped["Book"] = relationship(  # type: ignore  # noqa: F821
        back_populates="copies"
    )

    loan: Mapped[list["Loan"]] = relationship(  # type: ignore  # noqa: F821
        back_populates="book_copy"
    )

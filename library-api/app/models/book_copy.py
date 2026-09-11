from enum import Enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CopyStatus(str, Enum):
    ACTIVE = "active"
    DAMAGED = "damaged"
    RETIRED = "retired"
    LOST = "lost"


class BookCopy(Base):
    __tablename__ = "book_copies"

    # -- COLUMNS -- #

    book_copy_id: Mapped[int] = mapped_column(primary_key=True)

    book_id: Mapped[int] = mapped_column(ForeignKey("books.book_id"), nullable=False)

    status: Mapped[CopyStatus] = mapped_column(
        SAEnum(CopyStatus, name="copy_status"),
        nullable=False,
        server_default=CopyStatus.ACTIVE,
    )

    # -- RELATIONSHIPS -- #

    book: Mapped["Book"] = relationship(back_populates="copies")  # type: ignore # noqa: F821

    loans: Mapped[list["Loan"]] = relationship(back_populates="book_copy")  # type: ignore # noqa: F821

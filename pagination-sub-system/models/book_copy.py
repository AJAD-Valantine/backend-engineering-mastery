from core.database import Base
from core.enums import CopyStatus
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class BookCopy(Base):
    __tablename__ = "book_copies"

    # -- COLUMNS -- #

    book_copy_id: Mapped[int] = mapped_column(primary_key=True)

    book_id: Mapped[int] = mapped_column(ForeignKey("books.book_id"), nullable=False)

    status: Mapped[CopyStatus] = mapped_column(
        Enum(CopyStatus, name="copy_status"),
        nullable=False,
        default=CopyStatus.ACTIVE,
        server_default=CopyStatus.ACTIVE,
    )

    # -- RELATIONSHIPS -- #

    book: Mapped["Book"] = relationship(back_populates="copies")  # type: ignore # noqa: F821

    loans: Mapped[list["Loan"]] = relationship(back_populates="book_copy")  # type: ignore # noqa: F821

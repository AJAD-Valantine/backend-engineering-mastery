import uuid
from datetime import UTC, datetime

from sqlalchemy import UUID, CheckConstraint, DateTime, ForeignKey, Index, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Loan(Base):
    __tablename__ = "loans"

    # -- COLUMNS -- #

    loan_id: Mapped[int] = mapped_column(primary_key=True)

    book_copy_id: Mapped[int] = mapped_column(
        ForeignKey("book_copies.book_copy_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    borrowed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    returned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=None
    )

    # -- RELATIONSHIPS -- #

    user: Mapped["User"] = relationship(  # type: ignore  # noqa: F821
        back_populates="loans"
    )

    book_copy: Mapped["BookCopy"] = relationship(  # type: ignore  # noqa: F821
        back_populates="loans"
    )

    # -- TABLE ARGS -- #

    __table_args__: tuple[CheckConstraint, CheckConstraint, Index] = (
        CheckConstraint(
            "borrowed_at < due_at",
            name="borrowed_at_lt_due_at",
        ),
        CheckConstraint(
            "returned_at IS NULL OR returned_at >= borrowed_at",
            name="returned_at_gte_borrowed_at",
        ),
        Index(
            "uq_active_loan_per_copy",
            "book_copy_id",
            unique=True,
            postgresql_where=text("returned_at IS NULL"),
            sqlite_where=text("returned_at IS NULL"),
        ),
    )

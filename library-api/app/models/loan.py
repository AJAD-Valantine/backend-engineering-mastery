import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Loan(Base):
    __tablename__ = "loans"

    loan_id: Mapped[int] = mapped_column(
        primary_key=True
        )

    book_copy_id: Mapped[int] = mapped_column(
        ForeignKey("book_copies.book_copy_id"),
        nullable=False
        )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False
    )

    borrowed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
        )

    returned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
        )

    user: Mapped["User"] = relationship(  # type: ignore  # noqa: F821
        back_populates="loans"
    )

    book_copy: Mapped["BookCopy"] = relationship(  # type: ignore  # noqa: F821
        back_populates="loan"
    )

import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True
        )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
        )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
        )

    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    phone: Mapped[str] = mapped_column(
        String(25),
        nullable=False
        )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
        )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="member"
        )

    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    loans: Mapped[list["Loan"]] = relationship(  # type: ignore  # noqa: F821
        back_populates="user"
    )

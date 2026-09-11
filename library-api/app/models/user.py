import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    UUID,
    CheckConstraint,
    DateTime,
    Index,
    String,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, Enum):
    MEMBER = "member"
    LIBRARIAN = "librarian"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    # -- COLUMNS -- #

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)

    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    phone: Mapped[str] = mapped_column(String(25), nullable=False)

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"),  # pyright: ignore[reportCallIssue] # type: ignore
        nullable=False,
        default=UserRole.MEMBER,
    )

    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=False,
        server_default=func.now(),
    )

    # -- RELATIONSHIPS -- #

    loans: Mapped[list["Loan"]] = relationship(  # type: ignore  # noqa: F821
        back_populates="user", cascade="save-update"
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(  # type: ignore  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )

    # -- TABLE ARGS -- #

    __table_args__ = (
        # Indexes
        Index("ix_users_active_role", "active", "role"),
        Index("ix_users_registered_at", "registered_at"),
        # Constraints
        CheckConstraint("char_length(first_name) >= 2", name="first_name_min"),
        CheckConstraint("char_length(last_name) >= 2", name="last_name_min"),
        CheckConstraint("char_length(phone) >= 7", name="phone_min"),
        CheckConstraint("char_length(email) >= 6", name="email_min"),
        CheckConstraint(
            "registered_at <= updated_at",
            name="registered_at_lte_updated_at",
        ),
    )

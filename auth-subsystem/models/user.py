import uuid
from datetime import datetime
from enum import Enum

from core.database import Base
from sqlalchemy import (
    UUID,
    DateTime,
    String,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserRole(str, Enum):
    MOD = "moderator"
    MEMBER = "member"
    LIBRARIAN = "super_admin"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)

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

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=False,
        server_default=func.now(),
    )

    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship( # type: ignore  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )

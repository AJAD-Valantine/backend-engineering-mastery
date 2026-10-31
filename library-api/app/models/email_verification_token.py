import uuid
from datetime import datetime

from sqlalchemy import UUID, CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.database import Base


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    # -- COLUMNS -- #

    email_verification_token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"), index=True, nullable=False
    )

    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
    )

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=None
    )

    # -- RELATIONSHIPS -- #

    user: Mapped["User"] = relationship(back_populates="email_verification_tokens")  # pyright: ignore[reportUndefinedVariable]  # noqa: F821

    # -- TABLE ARGS -- #

    __table_args__ = (
        CheckConstraint(
            "used_at <= expires_at",
            name="used_at_lte_expires_at",
        ),
    )

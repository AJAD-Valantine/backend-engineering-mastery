import uuid
from datetime import datetime

from core.database import Base
from sqlalchemy import UUID, DateTime, ForeignKey, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    password_reset_token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), index=True, nullable=False
    )

    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=None
    )

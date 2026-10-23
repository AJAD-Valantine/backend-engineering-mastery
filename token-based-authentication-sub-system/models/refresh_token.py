import uuid
from datetime import datetime

from core.database import Base
from sqlalchemy import UUID, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    refresh_token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
    )

    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
    )

    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        default="unknown",
    )

    user_agent: Mapped[str] = mapped_column(
        String(255), nullable=False, default="unknown"
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

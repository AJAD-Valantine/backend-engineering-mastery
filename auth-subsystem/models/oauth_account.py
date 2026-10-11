import uuid

from core.database import Base
from sqlalchemy import UUID, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    oauth_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), index=True, nullable=False
    )

    # "google", "github", etc.
    oauth_name: Mapped[str] = mapped_column(String(50), nullable=False)

    # The unique ID provided by Google or GitHub
    account_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    # The email associated with the third-party account
    account_email: Mapped[str] = mapped_column(String(100), nullable=False)

    user: Mapped["User"] = relationship(back_populates="oauth_accounts")  # pyright: ignore[reportUndefinedVariable] # noqa: F821

    # A user can only have one linked account per provider (e.g., one Google account)
    __table_args__ = (
        UniqueConstraint("oauth_name", "account_id", name="uix_oauth_account"),
    )

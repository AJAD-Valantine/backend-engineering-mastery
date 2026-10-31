from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, token: PasswordResetToken) -> PasswordResetToken:

        self.db.add(token)
        self.db.flush()
        self.db.refresh(token)

        return token

    def read_by_hash(self, token_hash: str) -> PasswordResetToken | None:

        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash
        )

        return self.db.scalar(stmt)

    def mark_as_used(self, token: PasswordResetToken) -> None:

        token.used_at = datetime.now(UTC)
        self.db.flush()

    def delete_by_user_id(self, user_id: UUID):

        stmt = delete(PasswordResetToken).where(PasswordResetToken.user_id == user_id)

        self.db.execute(stmt)

from datetime import UTC, datetime
from uuid import UUID

from models.email_verification_token import EmailVerificationToken
from sqlalchemy import delete, select
from sqlalchemy.orm import Session


class EmailVerificationTokenRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, token: EmailVerificationToken) -> EmailVerificationToken:

        self.db.add(token)
        self.db.flush()
        self.db.refresh(token)

        return token

    def read_by_hash(self, token_hash: str) -> EmailVerificationToken | None:

        stmt = select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == token_hash
        )

        return self.db.scalar(stmt)

    def mark_as_used(self, token: EmailVerificationToken) -> None:

        token.used_at = datetime.now(UTC)
        self.db.flush()

    def delete_all_pending_for_user(self, user_id: UUID) -> None:
        stmt = delete(EmailVerificationToken).where(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.used_at.is_(None),
        )
        self.db.execute(stmt)
        self.db.flush()

from datetime import UTC, datetime

from models.email_verification_token import EmailVerificationToken
from sqlalchemy import select
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

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session) -> None:
        self.db: Session = db

    def create(self, token: RefreshToken) -> RefreshToken:

        self.db.add(token)
        self.db.flush()
        self.db.refresh(token)

        return token

    def read_by_hash(self, token_hash: str) -> RefreshToken | None:

        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)

        return self.db.scalar(stmt)

    def revoke(self, token: RefreshToken) -> None:

        token.revoked_at = datetime.now(UTC)
        self.db.flush()

    def revoke_all_for_user(self, user_id: UUID) -> None:

        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )

        self.db.execute(stmt)
        self.db.flush()

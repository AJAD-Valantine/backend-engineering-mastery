from uuid import UUID

from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetTokens


class PasswordResetTokenRepository:

    def __init__(
            self,
            db: Session
    ) -> None:
        self.db = db

    def create_token(
            self,
            token: PasswordResetTokens
    ) -> PasswordResetTokens:

        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)

        return token

    def get_by_hash(
            self,
            token_hash: str
    ) -> PasswordResetTokens | None:

        return self.db.query(PasswordResetTokens).filter(
            PasswordResetTokens.token_hash == token_hash
        ).first()

    def delete_by_user_id(
            self,
            user_id: UUID
    ) -> None:

        self.db.query(PasswordResetTokens).filter(
            PasswordResetTokens.user_id == user_id
        ).delete()
        self.db.commit()

    def delete_token(
            self,
            token: PasswordResetTokens
    ) -> None:

        self.db.delete(token)
        self.db.commit()
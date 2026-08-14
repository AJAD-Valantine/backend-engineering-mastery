from datetime import datetime, UTC, timedelta

from app.core import security
from app.core.config import settings
from app.exceptions.user import InvalidCredentials, InvalidOrExpiredResetToken, UserNotFound, IncorrectPassword
from app.models import PasswordResetTokens
from app.models.user import Users
from app.repository.password_reset_token import PasswordResetTokenRepository
from app.schemas.auth import Token
from app.schemas.user import UserCreateRequest
from app.repository.user import UserRepository
from app.services.user import UserService


class AuthService:

    def __init__(
            self,
            user_repository : UserRepository,
            user_service : UserService,
            reset_token_repository : PasswordResetTokenRepository
    ):
        self.user_repository = user_repository
        self.user_service = user_service
        self.reset_token_repository = reset_token_repository


    def register_user(
            self,
            request: UserCreateRequest
    ) -> Users:

        return self.user_service.add_user(request)


    def authenticate_user(
            self,
            email: str,
            plain_password: str
    ) -> Token:

        user = self.user_repository.read_user_by_email(email)

        if user is None or not security.verify_password(
                plain_password,
                user.hashed_password
        ):
            raise InvalidCredentials

        payload = {"sub": str(user.user_id)}
        token = security.create_access_token(payload)

        return Token(
            access_token=token,
            token_type="bearer"
        )


    def request_password_reset(
            self,
            email: str
    ) -> str | None:

        user = self.user_repository.read_user_by_email(email)
        if user is None:
            return None  # router decides what to tell the client — see below

        self.reset_token_repository.delete_by_user_id(user.user_id)

        raw_token = security.generate_reset_token()
        token = PasswordResetTokens(
            user_id=user.user_id,
            token_hash=security.hash_reset_token(raw_token),
            expires_at=datetime.now(UTC) + timedelta(minutes=settings.reset_token_expire_minutes),
        )
        self.reset_token_repository.create_token(token)
        return raw_token


    def reset_password(
            self,
            token: str,
            new_password: str
    ) -> None:

        token_hash = security.hash_reset_token(token)
        reset_token = self.reset_token_repository.get_by_hash(token_hash)

        if reset_token is None:
            raise InvalidOrExpiredResetToken

        if reset_token.expires_at < datetime.now(UTC):
            self.reset_token_repository.delete_token(reset_token)
            raise InvalidOrExpiredResetToken

        user = self.user_repository.read_user_by_id(reset_token.user_id)
        if user is None:
            raise InvalidOrExpiredResetToken

        self.user_repository.update_user(
            user_id=user.user_id,
            update_data={"hashed_password": security.hash_password(new_password)}
        )
        self.reset_token_repository.delete_by_user_id(user.user_id)


    def change_password(
            self,
            user_id,
            current_password: str,
            new_password: str
    ) -> None:

        user = self.user_repository.read_user_by_id(user_id)
        if user is None:
            raise UserNotFound

        if not security.verify_password(
                plain_password=current_password,
                hashed_password=user.hashed_password
        ):
            raise IncorrectPassword

        self.user_repository.update_user(
            user_id=user_id,
            update_data={"hashed_password": security.hash_password(new_password)}
        )
        self.reset_token_repository.delete_by_user_id(user_id)
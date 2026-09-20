from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status

from app.core import security
from app.core.config import Settings
from app.core.email import send_reset_email
from app.models.password_reset_token import PasswordResetToken
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repository.email_verification_repository import (
    EmailVerificationTokenRepository,
)
from app.repository.password_reset_token import PasswordResetTokenRepository
from app.repository.refresh_token import RefreshTokenRepository
from app.repository.user import UserRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreateRequest
from app.services.user import UserService

from ..models.email_verification_token import EmailVerificationToken

settings = Settings()  # type: ignore


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        user_service: UserService,
        refresh_token_repository: RefreshTokenRepository,
        password_reset_token_repository: PasswordResetTokenRepository,
        email_verification_token_repository: EmailVerificationTokenRepository,
    ) -> None:

        self.user_repository = user_repository
        self.user_service = user_service
        self.refresh_token_repository = refresh_token_repository
        self.password_reset_token_repository = password_reset_token_repository
        self.email_verification_token_repository = email_verification_token_repository

    def register_user(self, request: UserCreateRequest) -> User:
        return self.user_service.add_user(request)

    def authenticate_user(
        self,
        email: str,
        plain_password: str,
    ) -> TokenResponse:

        user: User | None = self.user_repository.read_by_email(email)

        if user is None or not security.verify_password(
            plain_password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token: str = security.create_access_token(user.user_id)
        refresh_token: str = security.generate_token()

        hashed_refresh_token: str = security.hash_token(refresh_token)

        now: datetime = datetime.now(UTC)

        token = RefreshToken(
            user_id=user.user_id,
            token_hash=hashed_refresh_token,
            expires_at=now + timedelta(days=settings.refresh_token_expire_days),
            created_at=now,
        )

        self.refresh_token_repository.create(token)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def refresh_tokens(self, raw_token: str) -> TokenResponse:

        token_hash: str = security.hash_token(raw_token)
        stored_refresh_token: RefreshToken | None = (
            self.refresh_token_repository.read_by_hash(token_hash)
        )

        if stored_refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if stored_refresh_token.revoked_at is not None:
            self.refresh_token_repository.revoke_all_for_user(
                stored_refresh_token.user_id
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if stored_refresh_token.expires_at < datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        self.refresh_token_repository.revoke(stored_refresh_token)

        new_access_token: str = security.create_access_token(
            stored_refresh_token.user_id
        )
        new_refresh_token: str = security.generate_token()

        hashed_refresh_token: str = security.hash_token(new_refresh_token)

        now: datetime = datetime.now(UTC)

        token = RefreshToken(
            user_id=stored_refresh_token.user_id,
            token_hash=hashed_refresh_token,
            expires_at=now + timedelta(days=settings.refresh_token_expire_days),
            created_at=now,
        )

        self.refresh_token_repository.create(token)

        return TokenResponse(
            access_token=new_access_token, refresh_token=new_refresh_token
        )

    # OPTION A — logs out this device only
    def logout(self, raw_token: str) -> None:

        token_hash: str = security.hash_token(raw_token)
        stored: RefreshToken | None = self.refresh_token_repository.read_by_hash(
            token_hash
        )

        if stored is None or stored.revoked_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        self.refresh_token_repository.revoke(stored)

    # OPTION B — logs out every device for this user
    def logout_all(self, raw_token: str) -> None:

        hashed_refresh_token: str = security.hash_token(raw_token)

        stored_refresh_token: RefreshToken | None = (
            self.refresh_token_repository.read_by_hash(hashed_refresh_token)
        )

        if stored_refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        self.refresh_token_repository.revoke_all_for_user(stored_refresh_token.user_id)

    def forgot_password(self, email: str) -> None:

        user: User | None = self.user_repository.read_by_email(email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password reset failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        raw_password_reset_token: str = security.generate_token()
        hashed_password_reset_token: str = security.hash_token(raw_password_reset_token)

        new_password_reset_token = PasswordResetToken(
            user_id=user.user_id,
            token_hash=hashed_password_reset_token,
            expires_at=datetime.now(UTC)
            + timedelta(minutes=settings.password_reset_expire_minutes),
        )

        self.password_reset_token_repository.create(new_password_reset_token)

        send_reset_email(user.email, raw_password_reset_token)

    def reset_password(self, raw_token: str, new_password: str) -> None:

        hashed_password_reset_token: str = security.hash_token(raw_token)
        stored_password_reset_token: PasswordResetToken | None = (
            self.password_reset_token_repository.read_by_hash(
                hashed_password_reset_token
            )
        )

        now: datetime = datetime.now(UTC)

        if (
            stored_password_reset_token is None
            or stored_password_reset_token.expires_at < now
            or stored_password_reset_token.used_at is not None
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password reset failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        new_hashed_password: str = security.hash_password(new_password)
        user: User | None = self.user_repository.read_by_id(
            stored_password_reset_token.user_id
        )

        if user is not None:
            self.user_repository.set_new_password(user, new_hashed_password)

        self.password_reset_token_repository.mark_as_used(stored_password_reset_token)

    def verify_email(self, raw_token: str) -> None:

        hashed_email_verification_token: str = security.hash_token(raw_token)

        stored_email_verification_token: EmailVerificationToken | None = (
            self.email_verification_token_repository.read_by_hash(
                hashed_email_verification_token
            )
        )

        now: datetime = datetime.now(UTC)

        if (
            stored_email_verification_token is None
            or stored_email_verification_token.expires_at < now
            or stored_email_verification_token.used_at is not None
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email verification failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user: User | None = self.user_repository.read_by_id(
            stored_email_verification_token.user_id
        )

        if user is not None:
            self.user_repository.verify_user(user)

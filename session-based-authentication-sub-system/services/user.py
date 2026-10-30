from datetime import UTC, datetime, timedelta

from core.config import Settings
from core.email import EmailManager
from core.security import SecurityManager
from fastapi import HTTPException, status
from models.email_verification_token import EmailVerificationToken
from models.user import User
from repositories.email_verification_token import (
    EmailVerificationTokenRepository,
)
from repositories.user import UserRepository
from schemas.user import UserCreateRequest


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        email_verification_token_repository: EmailVerificationTokenRepository,
        settings: Settings,
        security_manager: SecurityManager,
        email_manager: EmailManager,
    ) -> None:

        self.user_repository = user_repository
        self.email_verification_token_repository = email_verification_token_repository
        self.settings = settings
        self.security_manager = security_manager
        self.email_manager = email_manager

    def add_user(self, user_data: UserCreateRequest, role="member") -> User:

        existing_user: User | None = self.user_repository.read_by_email(user_data.email)

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
            )

        hashed_password: str = self.security_manager.hash_password(user_data.password)

        new_user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            hashed_password=hashed_password,
            role=role,
        )

        user: User = self.user_repository.create(new_user)

        email_verification_token: str = self.security_manager.generate_token()
        hashed_email_verification_token: str = self.security_manager.hash_token(
            email_verification_token
        )

        new_email_verification_token = EmailVerificationToken(
            user_id=user.user_id,
            token_hash=hashed_email_verification_token,
            expires_at=datetime.now(UTC)
            + timedelta(days=self.settings.email_verification_token_expire_days),
        )

        self.email_verification_token_repository.create(new_email_verification_token)

        self.email_manager.send_verification_email(user.email, email_verification_token)

        return user

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status

from app.core import security
from app.core.config import get_settings
from app.core.email import send_verification_email
from app.core.security import hash_password
from app.models.email_verification_token import EmailVerificationToken
from app.models.user import User, UserRole
from app.repository.email_verification_repository import (
    EmailVerificationTokenRepository,
)
from app.repository.password_reset_token import PasswordResetTokenRepository
from app.repository.refresh_token import RefreshTokenRepository
from app.repository.user import UserRepository
from app.schemas.user import UserCreateRequest, UserUpdateRequest


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        email_verification_repository: EmailVerificationTokenRepository,
        refresh_token_repository: RefreshTokenRepository,
        password_reset_token_repository: PasswordResetTokenRepository
    ) -> None:
        self.user_repository = user_repository
        self.email_verification_repository = email_verification_repository
        self.refresh_token_repository = refresh_token_repository
        self.password_reset_token_repository = password_reset_token_repository
        self.settings = get_settings()

    def add_user(
        self,
        user_data: UserCreateRequest,
        role: str | UserRole = UserRole.MEMBER,
    ) -> User:
        existing_user: User | None = self.user_repository.read_by_email(user_data.email)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

        hashed_pwd: str = hash_password(user_data.password)

        assigned_role: UserRole = role if isinstance(role, UserRole) else UserRole(role)

        new_user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            address=getattr(user_data, "address", None),
            email=user_data.email,
            hashed_password=hashed_pwd,
            role=assigned_role,
        )

        user: User = self.user_repository.create(new_user)

        email_verification_token: str = security.generate_token()
        hashed_email_verification_token: str = security.hash_token(
            email_verification_token
        )

        new_email_verification_token = EmailVerificationToken(
            user_id=user.user_id,
            token_hash=hashed_email_verification_token,
            expires_at=datetime.now(UTC)
            + timedelta(days=self.settings.email_verification_token_expire_days),
        )

        self.email_verification_repository.create(new_email_verification_token)

        send_verification_email(user.email, email_verification_token)

        return user

    def get_user_by_id(self, user_id: UUID) -> User:
        user: User | None = self.user_repository.read_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
        return user

    def update_user(self, user_id: UUID, new_data: UserUpdateRequest) -> User:

        updated_data = new_data.model_dump(exclude_unset=True)

        user: User | None = self.user_repository.read_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )

        return self.user_repository.update(user, updated_data)

    def get_user_by_email(self, email: str) -> User:
        user: User | None = self.user_repository.read_by_email(email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{email}' not found",
            )
        return user

    def deactivate_user_account(self, user_id: UUID) -> None:

        user: User | None = self.user_repository.read_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )

        for loan in user.loans:
            if loan.returned_at is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"User with ID {user_id} has un returned loan(s)",
                )

        self.refresh_token_repository.revoke_all_for_user(user.user_id)
        self.user_repository.deactivate(user)

    def change_user_role(self, user_id: UUID, role: UserRole) -> User:

        user: User | None = self.user_repository.read_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )

        return self.user_repository.change_role(user, role)


    def activate_user_account(self, user_id: UUID) -> User:

        user: User | None = self.user_repository.read_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )

        return self.user_repository.activate(user)

    def hard_delete_user_account(self, user_id: UUID):
        user: User | None = self.user_repository.read_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )

        self.user_repository.delete(user)


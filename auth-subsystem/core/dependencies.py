from collections.abc import Generator
from functools import lru_cache
from typing import Annotated, Any

from core.config import Settings
from core.database import SessionLocal
from core.email import EmailManager
from core.security import SecurityManager
from fastapi import Depends
from repositories.email_verification_token import (
    EmailVerificationTokenRepository,
)
from repositories.password_reset_token import PasswordResetTokenRepository
from repositories.refresh_token import RefreshTokenRepository
from repositories.user import UserRepository
from services.auth import AuthService
from services.user import UserService
from sqlalchemy.orm import Session


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]


SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_security_manager(settings: SettingsDep) -> SecurityManager:
    return SecurityManager(settings)


SecurityManagerDep = Annotated[SecurityManager, Depends(get_security_manager)]

def get_email_manager(settings: SettingsDep) -> EmailManager:
    return EmailManager(settings)


EmailManagerDep = Annotated[EmailManager, Depends(get_email_manager)]


def get_db() -> Generator[Session, Any, None]:
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]


def get_user_repository(db: SessionDep) -> UserRepository:
    return UserRepository(db)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_email_verification_token_repository(
    db: SessionDep,
) -> EmailVerificationTokenRepository:

    return EmailVerificationTokenRepository(db)


EmailVerificationTokenRepositoryDep = Annotated[
    EmailVerificationTokenRepository,
    Depends(get_email_verification_token_repository),
]


def get_user_service(
    user_repository: UserRepositoryDep,
    settings: SettingsDep,
    email_verification_token_repository: EmailVerificationTokenRepositoryDep,
    security_manager: SecurityManagerDep,
    email_manager: EmailManagerDep,
) -> UserService:
    from services.user import UserService

    return UserService(
        user_repository=user_repository,
        email_verification_token_repository=email_verification_token_repository,
        settings=settings,
        security_manager=security_manager,
        email_manager=email_manager,
    )


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_refresh_token_repository(db: SessionDep) -> RefreshTokenRepository:
    return RefreshTokenRepository(db)


RefreshTokenRepositoryDep = Annotated[
    RefreshTokenRepository,
    Depends(get_refresh_token_repository),
]


def get_password_reset_token_repository(
    db: SessionDep,
) -> PasswordResetTokenRepository:
    return PasswordResetTokenRepository(db)


PasswordResetTokenRepositoryDep = Annotated[
    PasswordResetTokenRepository,
    Depends(get_password_reset_token_repository),
]


def get_auth_service(
    user_service: UserServiceDep,
    user_repository: UserRepositoryDep,
    email_verification_token_repository: EmailVerificationTokenRepositoryDep,
    refresh_token_repository: RefreshTokenRepositoryDep,
    password_reset_token_repository: PasswordResetTokenRepositoryDep,
    settings: SettingsDep,
    security_manager: SecurityManagerDep,
    email_manager: EmailManagerDep,
) -> AuthService:
    return AuthService(
        user_service=user_service,
        user_repository=user_repository,
        email_verification_token_repository=email_verification_token_repository,
        refresh_token_repository=refresh_token_repository,
        password_reset_token_repository=password_reset_token_repository,
        settings=settings,
        security_manager=security_manager,
        email_manager=email_manager,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

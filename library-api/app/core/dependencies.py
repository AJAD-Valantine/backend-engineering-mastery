from collections.abc import Generator
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.database import SessionLocal
from app.models.user import User
from app.repository.book import BookRepository
from app.repository.email_verification_repository import (
    EmailVerificationTokenRepository,
)
from app.repository.password_reset_token import PasswordResetTokenRepository
from app.repository.refresh_token import RefreshTokenRepository
from app.repository.user import UserRepository
from app.services.auth import AuthService
from app.services.book import BookService
from app.services.user import UserService


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


def get_email_verification_token_repository(
    db: SessionDep,
) -> EmailVerificationTokenRepository:
    return EmailVerificationTokenRepository(db)


EmailVerificationTokenRepositoryDep = Annotated[
    EmailVerificationTokenRepository,
    Depends(get_email_verification_token_repository),
]


def get_user_repository(db: SessionDep) -> UserRepository:
    return UserRepository(db)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_password_reset_token_repository(
    db: SessionDep,
) -> PasswordResetTokenRepository:
    return PasswordResetTokenRepository(db)


PasswordResetTokenRepositoryDep = Annotated[
    PasswordResetTokenRepository,
    Depends(get_password_reset_token_repository),
]


def get_refresh_token_repository(db: SessionDep) -> RefreshTokenRepository:
    return RefreshTokenRepository(db)


RefreshTokenRepositoryDep = Annotated[
    RefreshTokenRepository,
    Depends(get_refresh_token_repository),
]


def get_user_service(
    user_repository: UserRepositoryDep,
    email_verification_token_repository: EmailVerificationTokenRepositoryDep,
) -> UserService:
    return UserService(user_repository, email_verification_token_repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_book_repository(db: SessionDep) -> BookRepository:
    return BookRepository(db)


BookRepositoryDep = Annotated[BookRepository, Depends(get_book_repository)]


def get_book_service(book_repository: BookRepositoryDep) -> BookService:
    return BookService(book_repository)


BookServiceDep = Annotated[BookService, Depends(get_book_service)]


def get_auth_service(
    user_repository: UserRepositoryDep,
    user_service: UserServiceDep,
    refresh_token_repository: RefreshTokenRepositoryDep,
    password_reset_token_repository: PasswordResetTokenRepositoryDep,
    email_verification_token_repository: EmailVerificationTokenRepositoryDep,
) -> AuthService:
    return AuthService(
        user_repository,
        user_service,
        refresh_token_repository,
        password_reset_token_repository,
        email_verification_token_repository,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
LoginFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repository: UserRepositoryDep,
) -> User:
    str_user_id: str = security.verify_access_token(token)

    try:
        uuid_user_id = UUID(str_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user: User | None = user_repository.read_by_id(uuid_user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]

from collections.abc import Callable, Generator
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core import security
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.repository.author import AuthorRepository
from app.repository.book import BookRepository
from app.repository.email_verification_repository import (
    EmailVerificationTokenRepository,
)
from app.repository.loan import LoanRepository
from app.repository.password_reset_token import PasswordResetTokenRepository
from app.repository.refresh_token import RefreshTokenRepository
from app.repository.user import UserRepository
from app.services.auth import AuthService
from app.services.author import AuthorService
from app.services.book import BookService
from app.services.loan import LoanService
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
    refresh_token_repository: RefreshTokenRepositoryDep,
    password_reset_token_repository: PasswordResetTokenRepositoryDep,
) -> UserService:
    return UserService(
        user_repository,
        email_verification_token_repository,
        refresh_token_repository,
        password_reset_token_repository,
    )


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_book_repository(db: SessionDep) -> BookRepository:
    return BookRepository(db)


BookRepositoryDep = Annotated[BookRepository, Depends(get_book_repository)]


def get_book_service(book_repository: BookRepositoryDep) -> BookService:
    return BookService(book_repository)


BookServiceDep = Annotated[BookService, Depends(get_book_service)]


def get_loan_repository(db: SessionDep) -> LoanRepository:
    return LoanRepository(db)


LoanRepositoryDep = Annotated[LoanRepository, Depends(get_loan_repository)]


def get_loan_service(
    loan_repository: LoanRepositoryDep,
    book_repository: BookRepositoryDep,
    user_repository: UserRepositoryDep,
) -> LoanService:
    return LoanService(loan_repository, book_repository, user_repository)


LoanServiceDep = Annotated[LoanService, Depends(get_loan_service)]


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

def get_author_repository(db: SessionDep) -> AuthorRepository:
    return AuthorRepository(db)

AuthorRepositoryDep = Annotated[AuthorRepository, Depends(get_author_repository)]

def get_author_service(author_repository: AuthorRepositoryDep) -> AuthorService:
    return AuthorService(author_repository)

AuthorServiceDep = Annotated[AuthorService, Depends(get_author_service)]


AccessTokenDep = Annotated[HTTPAuthorizationCredentials, HTTPBearer()]


def get_current_user(
    credentials: AccessTokenDep,
    user_repository: UserRepositoryDep,
) -> User:

    token: str = credentials.credentials
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


def require_roles(*allowed_roles: UserRole) -> Callable[..., User]:
    def role_checker(
        current_user: CurrentUserDep,
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker


RequireRoleDep = Annotated[User, Depends(require_roles)]

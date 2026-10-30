from collections.abc import AsyncGenerator, Generator
from functools import lru_cache
from typing import Annotated, Any

import httpx
from core.config import Settings
from core.email import EmailManager
from core.postgres import SessionLocal
from core.redis import redis_client
from core.security import SecurityManager
from fastapi import Cookie, Depends, HTTPException, Request, status
from models.user import User
from redis import Redis
from repositories.email_verification_token import (
    EmailVerificationTokenRepository,
)
from repositories.password_reset_token import PasswordResetTokenRepository
from repositories.session import SessionRepository
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

def get_redis() -> Redis:
    return redis_client

RedisDep = Annotated[Redis, Depends(get_redis)]

def get_session_repository(redis: RedisDep, settings: SettingsDep) -> SessionRepository:
    return SessionRepository(redis_client=redis, settings=settings)

SessionRepositoryDep = Annotated[SessionRepository, Depends(get_session_repository)]

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


async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient() as client:
        yield client


HttpClientDep = Annotated[httpx.AsyncClient, Depends(get_http_client)]


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
    password_reset_token_repository: PasswordResetTokenRepositoryDep,
    settings: SettingsDep,
    session_repository: SessionRepositoryDep,
    security_manager: SecurityManagerDep,
    email_manager: EmailManagerDep,
    request: Request,
) -> AuthService:

    client_ip: str = request.client.host if request.client else "unknown"
    user_agent: str = request.headers.get("user-agent", "unknown")

    return AuthService(
        user_service=user_service,
        user_repository=user_repository,
        session_repository=session_repository,
        email_verification_token_repository=email_verification_token_repository,
        password_reset_token_repository=password_reset_token_repository,
        settings=settings,
        security_manager=security_manager,
        email_manager=email_manager,
        client_ip=client_ip,
        user_agent=user_agent,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

settings: Settings = get_settings()

SessionCookieDep = Annotated[str | None, Cookie(alias=settings.session_cookie_name)]


def get_current_user(
    user_repository: UserRepositoryDep,
    session_repository: SessionRepositoryDep,
    session_id: SessionCookieDep = None,
) -> User:

    if session_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )

    session_data: dict[str, Any] | None = session_repository.get_session(session_id)

    if session_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )

    user_id = session_data.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )

    user: User | None = user_repository.read_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    session_repository.refresh_session_ttl(session_id)

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]

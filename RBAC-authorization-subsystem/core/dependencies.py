from collections.abc import Generator
from functools import lru_cache
from typing import Annotated, Any
from uuid import UUID

from core.config import Settings
from core.database import SessionLocal
from core.enums import Permission, UserRole
from core.permissions import get_inherited_roles, has_permission
from core.security import SecurityManager
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.user import User
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


def get_user_service(
    user_repository: UserRepositoryDep,
    settings: SettingsDep,
    security_manager: SecurityManagerDep,
) -> UserService:
    from services.user import UserService

    return UserService(
        user_repository=user_repository,
        settings=settings,
        security_manager=security_manager,
    )


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_auth_service(
    user_service: UserServiceDep,
    user_repository: UserRepositoryDep,
    settings: SettingsDep,
    security_manager: SecurityManagerDep,
    request: Request,
) -> AuthService:

    client_ip: str = request.client.host if request.client else "unknown"
    user_agent: str = request.headers.get("user-agent", "unknown")

    return AuthService(
        user_service=user_service,
        user_repository=user_repository,
        settings=settings,
        security_manager=security_manager,
        client_ip=client_ip,
        user_agent=user_agent,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


AccessTokenDep = Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())]


def get_current_user(
    auth_header: AccessTokenDep,
    user_repository: UserRepositoryDep,
    security_manager: SecurityManagerDep,
) -> User:

    token: str = auth_header.credentials

    str_user_id: str = security_manager.verify_access_token(token)

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


def require_role_or_above(minimum_role: UserRole):

    def role_checker(current_user: CurrentUserDep) -> User:
        user_role = current_user.role

        if user_role == minimum_role:
            return current_user

        if minimum_role in get_inherited_roles(user_role):
            return current_user

        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return role_checker


def require_permission(*permissions: Permission):

    def permission_checker(
        current_user: CurrentUserDep,
    ) -> User:
        for permission in permissions:
            if not has_permission(current_user.role, permission):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return permission_checker


def get_owner_or_official(model, id_param: str, *roles):

    def checker(
        request: Request,
        current_user: CurrentUserDep,
        db: SessionDep,
    ):
        resource_id = request.path_params[id_param]
        resource = db.get(model, resource_id)

        if resource is None:
            raise HTTPException(status_code=404)

        if current_user.role in roles:
            return resource

        if resource.user_id != current_user.user_id:
            raise HTTPException(status_code=404)

        return resource

    return checker

from core.config import Settings
from core.security import SecurityManager
from fastapi import HTTPException, status
from models.user import User
from repositories.user import UserRepository
from schemas.auth import TokenResponse
from schemas.user import UserCreateRequest
from services.user import UserService


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        user_service: UserService,
        settings: Settings,
        security_manager: SecurityManager,
        client_ip: str,
        user_agent: str,
    ) -> None:

        self.user_repository = user_repository
        self.user_service = user_service
        self.settings = settings
        self.security_manager = security_manager
        self.client_ip = client_ip
        self.user_agent = user_agent

    def register_user(self, request: UserCreateRequest) -> User:
        return self.user_service.add_user(request)



    def authenticate_user(
        self,
        email: str,
        plain_password: str,
    ) -> TokenResponse:

        user: User | None = self.user_repository.read_by_email(email)

        if user is None or not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email verification required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user is None or not self.security_manager.verify_password(
            plain_password, user.hashed_password # pyright: ignore[reportArgumentType]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token: str = self.security_manager.create_access_token(user.user_id, user.role)

        return TokenResponse(access_token=access_token)


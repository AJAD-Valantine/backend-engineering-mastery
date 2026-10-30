from core.config import Settings
from core.enums import UserRole
from core.security import SecurityManager
from fastapi import HTTPException, status
from models.user import User
from repositories.user import UserRepository
from schemas.user import UserCreateRequest, UserCreateRequestWithRole


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        settings: Settings,
        security_manager: SecurityManager,
    ) -> None:

        self.user_repository = user_repository
        self.settings = settings
        self.security_manager = security_manager

    def add_user(self, user_data: UserCreateRequest | UserCreateRequestWithRole) -> User:

        existing_user: User | None = self.user_repository.read_by_email(user_data.email)

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
            )

        hashed_password: str = self.security_manager.hash_password(user_data.password)

        user_role = getattr(user_data, "role", UserRole.USER)

        new_user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_role,
        )

        user: User = self.user_repository.create(new_user)

        return user

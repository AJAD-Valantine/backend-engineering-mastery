from fastapi import HTTPException, status

from app.core import security
from app.models.user import Users
from app.repository.user import UserRepository
from app.schemas.auth import Token
from app.schemas.user import UserCreateRequest
from app.services.user import UserService


class AuthService:

    def __init__(
            self,
            user_repository : UserRepository,
            user_service : UserService
    ) -> None:
        self.user_repository: UserRepository = user_repository
        self.user_service: UserService = user_service


    def register_user(
            self,
            request: UserCreateRequest
    ) -> Users:

        return self.user_service.add_user(request)


    def authenticate_user(
            self,
            email: str,
            plain_password: str
    ) -> Token:

        user: Users | None = self.user_repository.read_user_by_email(email)

        if user is None or not security.verify_password(
                plain_password,
                user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        payload: dict[str, str] = {"sub": str(user.user_id)}
        token: str = security.create_access_token(payload)

        return Token(
            access_token=token,
            token_type="bearer"
        )

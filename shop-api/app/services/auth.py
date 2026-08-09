from sqlalchemy.orm import Session

from app.core import security
from app.exceptions.user import (
    InvalidCredentials,
)
from app.models.user import Users
from app.schemas.auth import Token
from app.schemas.user import UserCreateRequest
from app.repository.user import UserRepository
from app.services.user import UserService


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.user_service = UserService()

    def register_new_user(self, db: Session, request: UserCreateRequest) -> Users:

        return self.user_service.add_user(db, request)     

    def authenticate_user(self, db: Session, email: str, plain_password: str) -> Token:
        user = self.user_repository.read_user_by_email(db, email)

        if user is None or not security.verify_password(plain_password, user.hashed_password):
            raise InvalidCredentials()
        
        payload = {"sub": str(user.user_id), "role": user.role}
        token = security.create_access_token(payload)

        return Token(access_token=token, token_type="bearer")
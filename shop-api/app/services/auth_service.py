from app.core import security
from app.models.user_model import Users
from app.presentation.schemas.user_schema import UserCreateRequest
from app.repository.user_repository import UserRepository
from app.services.user_service import UserService
from sqlalchemy.orm import Session


class AuthService:

    def __init__(self):
        self.user_repository = UserRepository()
        self.user_service = UserService()

    def register_new_user(self, db: Session, request: UserCreateRequest) -> Users:

        return self.user_service.add_user(db, request)     

    def authenticate_user(self, db: Session, email: str, plain_password: str):

        user = self.user_repository.read_user_by_email(db, email)

        if user is None:
            return 

        if security.verify_password(plain_password, user.hashed_password):
            return user

        return None        
from app.core import security
from app.exceptions.user_exceptions import EmailAlreadyExits
from app.models.user_model import Users
from app.presentation.schemas.user_schema import UserCreateRequest
from app.repository.user_repository import UserRepository
from sqlalchemy.orm import Session


class AuthService:

    def __init__(self):
        self.user_repository = UserRepository()

    def register_new_user(self, db: Session, request: UserCreateRequest) -> Users:

        if self.user_repository.read_user_by_email(db, request.email) is not None:
            raise EmailAlreadyExits("email already exists")

        hashed_password = security.hash_password(request.password)

        new_user = Users(
            first_name = request.first_name,
            last_name = request.last_name,            
            email = request.email,
            password_hash = hashed_password,
            phone = request.phone,
            address = request.address
        )

        return self.user_repository.create_user(db, new_user)

        

    def authenticate_user(self, db: Session, email: str, plain_password: str):

        user = self.user_repository.read_user_by_email(db, email)

        if user is None:
            return 

        if security.verify_password(plain_password, user.hashed_password):
            return user

        return None        
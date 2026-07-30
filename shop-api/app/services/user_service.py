import uuid

from app.exceptions.user_exceptions import EmailAlreadyExits, UserNotFound
from app.models.user_model import Users
from app.presentation.schemas.user_schema import (
    UserCreateRequest,
    UserUpdateRequest,
)
from app.repository.user_repository import UserRepository


class UserService:
    def __init__(self) -> None:
        self.user_repository = UserRepository()

    def add_user(self, db, user: UserCreateRequest):

        if (
            self.user_repository.read_user_by_email(db, user.email)
            is not None
        ):
            raise EmailAlreadyExits("email already exits.")

        user_id = uuid.uuid4()

        data = Users(
            user_id=user_id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            address=user.address,
        )

        return self.user_repository.create_user(db, data)

    def get_all_users(self, db):

        return self.user_repository.read_all_users(db)

    def get_user_by_id(self, db, user_id):

        user = self.user_repository.read_user_by_id(db, user_id)

        if user is None:
            raise UserNotFound("user not found")

        return user

    def update_user(self, db, user_id, request: UserUpdateRequest):

        user = self.user_repository.read_user_by_id(db, user_id)

        if user is None:
            raise UserNotFound("user not found")

        return self.user_repository.update_user(db, user_id, request)

    def remove_user(self, db, user_id):

        user = self.user_repository.read_user_by_id(db, user_id)

        if user is None:
            raise UserNotFound("user not found")

        return self.user_repository.delete_user(db, user_id)

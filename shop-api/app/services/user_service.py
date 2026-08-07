import uuid

from app.core.security import hash_password
from app.exceptions.user_exceptions import EmailAlreadyExits, UserNotFound
from app.models.user_model import Users
from app.repository.user_repository import UserRepository
from app.schemas.user_schema import (
    UserCreateRequest,
    UserUpdateRequest,
)


class UserService:
    
    def __init__(self) -> None:
        self.user_repository = UserRepository()

    def add_user(self, db, user: UserCreateRequest, role : str = "customer"):

        if (
            self.user_repository.read_user_by_email(db, user.email)
            is not None
        ):
            raise EmailAlreadyExits("email already exits.")

        user_id = uuid.uuid4()

        hashed_password = hash_password(user.password)

        data = Users(
            user_id=user_id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            address=user.address,
            hashed_password=hashed_password,
            role=role
        )

        return self.user_repository.create_user(db, data)

    def get_all_users(self, db, page: int = 1, size: int = 10):
        
        skip = (page - 1) * size
        
        total_items, users = self.user_repository.read_all_users(db, skip=skip, limit=size)
        
        return {
            "total_items": total_items,
            "page": page,
            "size": size,
            "data": users
        }

    def get_user_by_id(self, db, user_id):

        user = self.user_repository.read_user_by_id(db, user_id)

        if user is None:
            raise UserNotFound("user not found")

        return user

    def update_user(self, db, user_id, request: UserUpdateRequest):

        user = self.user_repository.read_user_by_id(db, user_id)

        if user is None:
            raise UserNotFound("user not found")

        update_data = request.model_dump(exclude_unset=True)

        return self.user_repository.update_user(db, user_id, update_data)

    def remove_user(self, db, user_id):

        user = self.user_repository.read_user_by_id(db, user_id)

        if user is None:
            raise UserNotFound("user not found")

        return self.user_repository.delete_user(db, user_id)

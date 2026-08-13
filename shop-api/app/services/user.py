import uuid

from app.core.security import hash_password
from app.exceptions.user import EmailAlreadyExits, UserNotFound
from app.models.user import Users
from app.repository.user import UserRepository
from app.schemas.user import (
    UserCreateRequest,
    UserUpdateRequest,
)


class UserService:
    
    def __init__(self, user_repository : UserRepository) -> None:
        self.user_repository = user_repository

    def add_user(
            self,
            user: UserCreateRequest,
            role : str = "customer"
    ):

        if self.user_repository.read_user_by_email(user.email) is not None:
            raise EmailAlreadyExits("email already exits.")

        user_id = uuid.uuid4()

        hashed_password = hash_password(user.password)

        user = Users(
            user_id=user_id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            address=user.address,
            hashed_password=hashed_password,
            role=role
        )

        return self.user_repository.create_user(user)

    def get_all_users(
            self,
            page: int = 1,
            size: int = 10
    ):

        skip = (page - 1) * size
        total_items, users = self.user_repository.read_all_users(
            skip=skip,
            limit=size
        )
        
        return {
            "total_items": total_items,
            "page": page,
            "size": size,
            "data": users
        }

    def get_user_by_id(
            self,
            user_id
    ):

        user = self.user_repository.read_user_by_id(user_id)

        if user is None:
            raise UserNotFound("user not found")

        return user

    def update_user(
            self,
            user_id,
            request: UserUpdateRequest
    ):

        user = self.user_repository.read_user_by_id(user_id)

        if user is None:
            raise UserNotFound("user not found")

        update_data = request.model_dump(exclude_unset=True)

        return self.user_repository.update_user(
            user_id=user_id,
            update_data=update_data
        )

    def remove_user(
            self,
            user_id
    ):

        user = self.user_repository.read_user_by_id(user_id)

        if user is None:
            raise UserNotFound("user not found")

        return self.user_repository.delete_user(user_id)
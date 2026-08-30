import uuid
from typing import Any
from uuid import UUID

from app.core.security import hash_password
from app.exceptions.user import EmailAlreadyExits, UserNotFound
from app.models.user import Users
from app.repository.user import UserRepository
from app.schemas.user import (
    UserCreateRequest,
    UserUpdateRequest,
)


class UserService:

    def __init__(
            self,
            user_repository : UserRepository
    ) -> None:
        self.user_repository: UserRepository = user_repository

    def add_user(
            self,
            user: UserCreateRequest,
            role : str = "customer"
    ) -> Users:

        if self.user_repository.read_user_by_email(user.email) is not None:
            raise EmailAlreadyExits()

        user_id: UUID = uuid.uuid4()
        hashed_password: str = hash_password(user.password)

        new_user = Users(
            user_id=user_id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            address=user.address,
            hashed_password=hashed_password,
            role=role
        )

        return self.user_repository.create_user(new_user)

    def get_all_users(self) -> list[Users]:

        return self.user_repository.read_all_users()

    def get_user_by_id(
            self,
            user_id : UUID
    ) -> Users:

        user: Users | None = self.user_repository.read_user_by_id(user_id)

        if user is None:
            raise UserNotFound("user not found")

        return user

    def update_user(
            self,
            user_id : UUID,
            request: UserUpdateRequest
    ) -> Users:

        user: Users | None = self.user_repository.read_user_by_id(user_id)

        if user is None:
            raise UserNotFound("user not found")

        update_data: dict[str, Any] = request.model_dump(exclude_unset=True)

        return self.user_repository.update_user(
            user=user,
            update_data=update_data
        )

    def remove_user(
            self,
            user_id
    ) -> None:

        user: Users | None = self.user_repository.read_user_by_id(user_id)

        if user is None:
            raise UserNotFound("user not found")

        self.user_repository.delete_user(user_id)

from uuid import UUID

from app.exceptions.base_exception import ShopException
from app.exceptions.user_exceptions import UserNotFound, EmailAlreadyExits
from app.presentation.schemas.user_schema import UserResponse
from app.presentation.schemas.response_model import error_response, success_response
from app.services.user_service import UserService


class UserController:
    def __init__(self) -> None:
        self.user_service = UserService()

    def create_user(self, db, request):

        try:
            raw_user = self.user_service.add_user(db, request)

            user = UserResponse.model_validate(raw_user).model_dump()
            return success_response(user, "user created successfully")

        except EmailAlreadyExits as e:
            return error_response(str(e), 400)

        except ShopException as e:
            return error_response(str(e), 500)

    def get_all_users(self, db):

        try:
            raw_users = self.user_service.get_all_users(db)
            users = [
                UserResponse.model_validate(user).model_dump()
                for user in raw_users
            ]

            if users:
                return success_response(users, "fetched all users")
            else:
                return error_response("no users available", 404)

        except ShopException as e:
            return error_response(str(e), 500)

    def get_user_by_id(self, db, user_id: UUID):

        try:
            raw_user = self.user_service.get_user_by_id(db, user_id)
            user = UserResponse.model_validate(raw_user).model_dump()
            return success_response(user, "fetched user")

        except UserNotFound as e:
            return error_response(str(e), 404)

        except ShopException as e:
            return error_response(str(e), 500)

    def update_user(self, db, user_id, request):

        try:
            raw_user = self.user_service.update_user(
                db, user_id, request
            )
            user = UserResponse.model_validate(raw_user).model_dump()
            return success_response(user, "user updated")

        except UserNotFound as e:
            return error_response(str(e), 404)

        except ShopException as e:
            return error_response(str(e), 500)

    def delete_user(self, db, user_id):

        try:
            raw_user = self.user_service.remove_user(db, user_id)
            user = UserResponse.model_validate(raw_user).model_dump()
            return success_response(user, "user deleted")

        except UserNotFound as e:
            return error_response(str(e), 404)

        except ShopException as e:
            return error_response(str(e), 500)

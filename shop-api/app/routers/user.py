from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from app.core.dependencies import (
    CurrentUser,
    get_user_service,
    require_admin,
)
from app.schemas.user import (
    AdminCreateUserRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.services.user import UserService

from ..models.user import Users

user_router = APIRouter(prefix="/users", tags=["Users"])


# Admin Only
@user_router.post(
    path="/create-user",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    dependencies=[Depends(require_admin)],
)
def create_user(
    request: AdminCreateUserRequest,
    user_service: UserService = Depends(get_user_service),
) -> Users:

    return user_service.add_user(request, request.role)


# Admin Only
@user_router.get(
    path="/get-all-users",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all users",
    dependencies=[Depends(require_admin)],
)
def get_all_users(
    user_service: UserService = Depends(get_user_service),
)   -> list[Users]:
    return user_service.get_all_users()


# Standard User Route
@user_router.get(
    path="/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get my profile",
)
def get_user(
    current_user: CurrentUser, user_service: UserService = Depends(get_user_service)
) -> Users:
    return user_service.get_user_by_id(current_user.user_id)


# Standard User Route
@user_router.patch(
    path="/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update my profile",
)
def update_user(
    request: UserUpdateRequest,
    current_user: CurrentUser,
    user_service: UserService = Depends(get_user_service),
) -> Users:
    return user_service.update_user(current_user.user_id, request)


# Admin Only
@user_router.delete(
    path="/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    dependencies=[Depends(require_admin)],
)
def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service)
    ) -> None:

    return user_service.remove_user(user_id)

from uuid import UUID

from fastapi import APIRouter, Depends, Query, UploadFile
from starlette import status

from app.core.config import settings
from app.core.dependencies import (
    CurrentUser,
    get_auth_service,
    get_user_service,
    require_admin,
)
from app.exceptions.image import FileTooLarge
from app.schemas.auth import ChangePasswordRequest
from app.schemas.user import (
    AdminCreateUserRequest,
    PaginatedUserResponse,
    UserResponse,
    UserUpdateRequest,
)
from app.services.auth import AuthService
from app.services.user import UserService

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
    request : AdminCreateUserRequest,
    user_service : UserService = Depends(get_user_service)

):

    return user_service.add_user(request, request.role)


# Admin Only
@user_router.get(
    path="/get-all-users",
    response_model=PaginatedUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all users",
    dependencies=[Depends(require_admin)],
)
def get_all_users(
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    user_service : UserService = Depends(get_user_service)

):
    return user_service.get_all_users(page=page, size=size)


# Standard User Route
@user_router.get(
    path="/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get my profile",
)
def get_user(
    current_user: CurrentUser,
    user_service : UserService = Depends(get_user_service)
): 
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
    user_service : UserService = Depends(get_user_service)
):  
    return user_service.update_user(current_user.user_id, request)

# Standard User Route
@user_router.patch(
    path="/me/password",
    status_code=status.HTTP_200_OK
)
def change_password(
    request: ChangePasswordRequest,
    current_user: CurrentUser,
    auth_service: AuthService = Depends(get_auth_service),
):
    auth_service.change_password(current_user.user_id, request.current_password, request.new_password)
    return {"message": "Password changed successfully"}


# Admin Only
@user_router.delete(
    path="/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    dependencies=[Depends(require_admin)],
)
def delete_user(
    user_id: UUID,
    user_service : UserService = Depends(get_user_service)
):
    return user_service.remove_user(user_id)

# Standard User Route
@user_router.patch(
    path="/me/picture",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
def upload_profile_picture(
        current_user: CurrentUser,
        file: UploadFile,
        user_service: UserService = Depends(get_user_service),
):
    if file.size and file.size > settings.max_upload_size_bytes:
        raise FileTooLarge()

    content = file.file.read()
    return user_service.upload_profile_image(current_user.user_id, content)

# Standard User Route
@user_router.delete(
    path="/me/picture",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_profile_picture(
        current_user: CurrentUser,
        user_service: UserService = Depends(get_user_service),
):
    user_service.remove_profile_image(current_user.user_id)
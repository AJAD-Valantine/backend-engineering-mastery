from uuid import UUID

from fastapi import APIRouter, Query, Depends
from starlette import status

from app.core.dependencies import DBSession, require_admin, CurrentUser
from app.schemas.user import (
    AdminCreateUserRequest,
    PaginatedUserResponse,
    UserUpdateRequest,
    UserResponse,
)
from app.services.user import UserService

user_router = APIRouter(prefix="/users", tags=["Users"])
user_service = UserService()


# Admin Only
@user_router.post(
    path="/create-user",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    dependencies=[Depends(require_admin)],
)
def create_user(
    request:AdminCreateUserRequest, 
    db: DBSession,
):  
    return user_service.add_user(db, request, request.role)


# Admin Only
@user_router.get(
    path="/get-all-users",
    response_model=PaginatedUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all users",
    dependencies=[Depends(require_admin)],
)
def get_all_users(
    db: DBSession,
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Items per page"),

):
    return user_service.get_all_users(db=db, page=page, size=size)


# Standard User Route
@user_router.get(
    path="/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get my profile",
)
def get_user(
    db: DBSession,
    current_user: CurrentUser
): 
    return user_service.get_user_by_id(db, current_user.user_id)


# Standard User Route
@user_router.patch(
    path="/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update my profile",
)
def update_user(
    request: UserUpdateRequest, 
    db: DBSession,
    current_user: CurrentUser
):  
    return user_service.update_user(db, current_user.user_id, request)


# Admin Only
@user_router.delete(
    path="/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    dependencies=[Depends(require_admin)],
)
def delete_user(
    user_id: UUID,
    db: DBSession,
):
    return user_service.remove_user(db, user_id)
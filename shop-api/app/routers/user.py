from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

from app.core.dependencies import db_connection, get_current_user
from app.models.user import Users
from app.schemas.user import (
    AdminCreateUserRequest,
    PaginatedUserResponse,
    UserUpdateRequest,
    UserResponse,
)
from app.services.user import UserService

user_router = APIRouter(prefix="/users", tags=["Users"])
user_service = UserService()


# RBAC pending
@user_router.post(
    path="/create-user",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    dependencies=[Depends(get_current_user)],
)
def create_user(
    request:AdminCreateUserRequest, 
    db: Session = Depends(db_connection),
):  
    return user_service.add_user(db, request, request.role)


# RBAC pending
@user_router.get(
    path="/get-all-users",
    response_model=PaginatedUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all users",
    dependencies=[Depends(get_current_user)],
)
def get_all_users(
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(db_connection),
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
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
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
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
):  
    return user_service.update_user(db, current_user.user_id, request)


# RBAC pending
@user_router.delete(
    path="/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    dependencies=[Depends(get_current_user)],
)
def delete_user(
    user_id: UUID,
    db: Session = Depends(db_connection),
):
    return user_service.remove_user(db, user_id)
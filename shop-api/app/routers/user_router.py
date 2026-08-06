from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import db_connection, get_current_user
from app.models.user_model import Users
from app.schemas.user_schema import (
    AdminCreateUserRequest,
    UserUpdateRequest,
)
from app.services.user_service import UserService

user_router = APIRouter(prefix="/users", tags=["Users"])
user_service = UserService()


# 🚨 Admin Only (RBAC pending)
@user_router.post("/create-user")
def create_user(
    request:AdminCreateUserRequest, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
):  
    return user_service.add_user(db, request, request.role)


# 🚨 Admin Only (RBAC pending)
@user_router.get("/get-all-users")
def get_all_users(
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
):
    return user_service.get_all_users(db)


# ✅ Standard User Route (View own profile)
@user_router.get("/me")
def get_user(
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return user_service.get_user_by_id(db, current_user.user_id)


# ✅ Standard User Route (Update own profile)
@user_router.patch("/me")
def update_user(
    request: UserUpdateRequest, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
):  
    return user_service.update_user(db, current_user.user_id, request)


# 🚨 Admin Only (RBAC pending)
@user_router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
):
    return user_service.remove_user(db, user_id)
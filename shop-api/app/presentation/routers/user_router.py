from uuid import UUID

from app.core.dependencies import db_connection, get_current_user
from app.models.user_model import Users
from app.presentation.controller.user_controller import UserController
from app.presentation.schemas.user_schema import (
    AdminCreateUserRequest,
    UserUpdateRequest,
)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

user_router = APIRouter(prefix="/users", tags=["Users"])
controller = UserController()


# 🚨 Admin Only (RBAC pending)
@user_router.post("/create-user")
def create_user(
    request:AdminCreateUserRequest, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
):  
    return controller.create_user(db, request)


# 🚨 Admin Only (RBAC pending)
@user_router.get("/get-all-users")
def get_all_users(
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
):
    return controller.get_all_users(db)


# ✅ Standard User Route (View own profile)
@user_router.get("/me")
def get_user(
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    # Fixes Pylance
    safe_uuid = UUID(str(current_user.user_id))
    return controller.get_user_by_id(db, safe_uuid)


# ✅ Standard User Route (Update own profile)
@user_router.patch("/me")
def update_user(
    request: UserUpdateRequest, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
):  
    # Fixes Pylance
    safe_uuid = UUID(str(current_user.user_id))
    return controller.update_user(db, safe_uuid, request)


# 🚨 Admin Only (RBAC pending)
@user_router.delete("/{user_id}")
def delete_user(
    user_id: UUID, # Grab the ID from the URL path!
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
):
    return controller.delete_user(db, user_id)
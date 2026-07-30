from uuid import UUID

from app.database import db_connection
from app.presentation.controller.user_controller import UserController
from app.presentation.schemas.user_schema import (
    UserCreateRequest,
    UserUpdateRequest,
)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

user_router = APIRouter(prefix="/users", tags=["Users"])
controller = UserController()


@user_router.post("/")
def create_user(request: UserCreateRequest, db: Session = Depends(db_connection)): # noqa: B008
    return controller.create_user(db, request)


@user_router.get("/")
def get_all_users(db: Session = Depends(db_connection)): # noqa: B008
    return controller.get_all_users(db)


@user_router.get("/{user_id}")
def get_user(user_id: UUID, db: Session = Depends(db_connection)): # noqa: B008
    return controller.get_user_by_id(db, user_id)


@user_router.patch("/{user_id}")
def update_user(user_id: UUID, request: UserUpdateRequest, db: Session = Depends(db_connection)): # noqa: B008
    return controller.update_user(db, user_id, request)


@user_router.delete("/{user_id}")
def delete_user(user_id: UUID, db: Session = Depends(db_connection)): # noqa: B008
    return controller.delete_user(db, user_id)

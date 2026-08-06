from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import db_connection
from app.schemas.auth_schema import Token
from app.schemas.user_schema import UserCreateRequest, UserResponse
from app.services.auth_service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()

@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(request: UserCreateRequest, db: Session = Depends(db_connection)):

    return auth_service.register_new_user(db, request)

@auth_router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_connection)):

    return auth_service.authenticate_user(db, form_data.username, form_data.password)
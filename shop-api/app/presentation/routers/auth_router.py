from app.core.dependencies import db_connection
from app.presentation.controller.auth_controller import AuthController
from app.presentation.schemas.auth_schema import Token
from app.presentation.schemas.user_schema import UserCreateRequest, UserResponse
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

auth_controller = AuthController()

@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(request: UserCreateRequest, db: Session = Depends(db_connection)): # noqa: B008
    """Registers a new user into the database."""
    return auth_controller.register(db, request)

@auth_router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_connection)): # noqa: B008
    """Authenticates a user and returns a JWT token."""
    return auth_controller.login(db, form_data)
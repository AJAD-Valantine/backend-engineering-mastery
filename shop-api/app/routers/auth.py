from fastapi import APIRouter, status

from app.core.dependencies import DBSession, OAuth2Form
from app.schemas.auth import Token
from app.schemas.user import UserCreateRequest, UserResponse
from app.services.auth import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()

@auth_router.post(
    path="/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user"
)
def register_user(
        request: UserCreateRequest,
        db: DBSession
):

    return auth_service.register_user(db, request)

@auth_router.post(
    path="/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User log in"
)
def login_user(
        db: DBSession,
        form_data: OAuth2Form,
):

    return auth_service.authenticate_user(
        db,
        form_data.username,
        form_data.password
    )
from fastapi import APIRouter, status, Depends

from app.core.dependencies import OAuth2Form, get_auth_service
from app.schemas.auth import Token
from app.schemas.user import UserCreateRequest, UserResponse
from app.services.auth import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post(
    path="/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user"
)
def register_user(
        request: UserCreateRequest,
        auth_service : AuthService = Depends(get_auth_service)
):

    return auth_service.register_user(request)

@auth_router.post(
    path="/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User log in"
)
def login_user(
        form_data: OAuth2Form,
        auth_service : AuthService = Depends(get_auth_service)
):

    return auth_service.authenticate_user(
        form_data.username,
        form_data.password
    )
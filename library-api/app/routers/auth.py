from fastapi import APIRouter, Depends, status

from app.core.dependencies import OAuth2Form, get_auth_service  # type: ignore
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
)
from app.schemas.user import UserCreateRequest, UserResponse
from app.services.auth import AuthService

from ..schemas.auth import TokenResponse

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post(
    path="/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
)
def register_user(
    request: UserCreateRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> User:

    return auth_service.register_user(request)




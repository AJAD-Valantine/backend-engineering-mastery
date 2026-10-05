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


@auth_router.post(
    path="/login",
    status_code=status.HTTP_200_OK,
    summary="User log in — returns access + refresh token",
)
def login_user(
    form_data: OAuth2Form,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:

    return auth_service.authenticate_user(form_data.username, form_data.password)


@auth_router.post(
    path="/refresh",
    status_code=status.HTTP_200_OK,
    summary="Rotate refresh token — returns new access + refresh token",
)
def refresh_tokens(
    body: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:

    return auth_service.refresh_tokens(body.refresh_token)


# OPTION A — keep this one if you want single-device logout
@auth_router.post(
    path="/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out this device",
)
def logout(
    body: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> None:

    auth_service.logout(body.refresh_token)


# OPTION B — keep this one (or replace the above) for all-device logout
@auth_router.post(
    path="/logout/all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out all devices",
)
def logout_all(
    body: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> None:

    auth_service.logout_all(body.refresh_token)


@auth_router.post("/forgot-password", status_code=204)
def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> None:

    auth_service.forgot_password(request.email)




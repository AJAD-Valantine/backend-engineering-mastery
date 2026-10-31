from fastapi import APIRouter, status

from app.core.dependencies import AuthServiceDep
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.user import UserCreateRequest, UserResponse

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post(
    path="/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
)
def register_user(
    request: UserCreateRequest,
    auth_service: AuthServiceDep,
) -> User:

    return auth_service.register_user(request)


@auth_router.post(
    path="/login",
    status_code=status.HTTP_200_OK,
    summary="User log in — returns access + refresh token",
)
def login_user(
    request_body: LoginRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:

    return auth_service.authenticate_user(request_body.email, request_body.password)


@auth_router.post(
    path="/refresh",
    status_code=status.HTTP_200_OK,
    summary="Rotate refresh token — returns new access + refresh token",
)
def refresh_tokens(
    body: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:

    return auth_service.refresh_tokens(body.refresh_token)


@auth_router.post(
    path="/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out this device",
)
def logout(
    body: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> None:

    auth_service.logout(body.refresh_token)


@auth_router.post(
    path="/logout/all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out all devices",
)
def logout_all(
    body: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> None:

    auth_service.logout_all(body.refresh_token)


@auth_router.post(
        path="/forgot-password",
        status_code=204
)
def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthServiceDep,
) -> None:

    auth_service.forgot_password(request.email)


@auth_router.post(
        path="/reset-password",
        status_code=204
)
def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthServiceDep,
) -> None:

    auth_service.reset_password(request.token, request.new_password)


@auth_router.get(
    path="/verify-email",
    status_code=status.HTTP_200_OK,
    summary="Verify user email via token link",
)
def verify_email(
    token: str,
    auth_service: AuthServiceDep,
) -> None:

    auth_service.verify_email(token)

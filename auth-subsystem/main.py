from collections.abc import Sequence
from typing import Any
from uuid import UUID

from core.database import Base, engine
from core.dependencies import AuthServiceDep, CurrentUserDep, HttpClientDep
from fastapi import Cookie, FastAPI, Response, status
from fastapi.responses import RedirectResponse
from models.email_verification_token import EmailVerificationToken  # noqa: F401
from models.oauth_account import OAuthAccount  # noqa: F401
from models.password_reset_token import PasswordResetToken  # noqa: F401
from models.refresh_token import RefreshToken
from models.user import User
from schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from schemas.user import UserCreateRequest, UserLoginRequest, UserResponse

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.post(
    path="/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register_user(
    request_body: UserCreateRequest,
    auth_service: AuthServiceDep,
) -> User:
    return auth_service.register_user(request_body)


@app.post(
    path="/verify-email",
    status_code=status.HTTP_200_OK,
    summary="Verify user email via token link",
)
def verify_email(
    token: str,
    auth_service: AuthServiceDep,
) -> None:

    auth_service.verify_email(token)


@app.post(
    path="/resend-verification",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Resend email verification link",
)
def resend_verification(
    request_body: ResendVerificationRequest,
    auth_service: AuthServiceDep,
) -> None:

    auth_service.resend_verification_email(request_body.email)


@app.post(
    path="/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login to the application",
)
def login_user(
    request_body: UserLoginRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    return auth_service.authenticate_user(request_body.email, request_body.password)


@app.post(
    path="/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh the authentication token",
)
def refresh_token(
    request_body: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    return auth_service.refresh_tokens(request_body.refresh_token)


@app.post(
    path="/logout",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out this device",
)
def logout(
    request_body: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> None:

    auth_service.logout(request_body.refresh_token)


@app.post(
    path="/logout/all",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out all devices",
)
def logout_all(
    request_body: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> None:

    auth_service.logout_all(request_body.refresh_token)


@app.post(
    path="/forgot-password",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Request a password reset link",
)
def forgot_password(
    request_body: ForgotPasswordRequest,
    auth_service: AuthServiceDep,
) -> None:

    auth_service.forgot_password(request_body.email)


@app.post(
    path="/reset-password",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reset the user's password",
)
def reset_password(
    request_body: ResetPasswordRequest,
    auth_service: AuthServiceDep,
) -> None:

    auth_service.reset_password(request_body.token, request_body.new_password)


@app.post(
    path="/change-password",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change the user's password",
)
def change_password(
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep,
    request_body: ChangePasswordRequest,
) -> None:

    auth_service.change_password(
        current_user, request_body.current_password, request_body.new_password
    )


@app.get(
    path="/sessions",
    response_model=list[RefreshTokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all active sessions for the current user",
)
def get_active_sessions(
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep,
) -> Sequence[RefreshToken]:

    return auth_service.get_active_sessions(current_user)


@app.delete(
    path="/sessions/{session_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out a specific session for the current user",
)
def logout_session(
    session_id: UUID,
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep,
) -> None:

    auth_service.logout_session(current_user, session_id)


@app.delete(
    path="/sessions",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out all sessions for the current user",
)
def logout_all_sessions(
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep,
) -> None:

    auth_service.logout_all_sessions(current_user)


@app.get(
    path="/auth/providers",
    status_code=status.HTTP_200_OK,
    summary="List available OAuth providers",
)
def get_providers() -> dict[str, list[str]]:
    return {"providers": ["google", "github"]}


@app.get(
    path="/auth/google",
    summary="Initiate Google OAuth2 flow",
    response_class=RedirectResponse,
)
def login_via_google(
    auth_service: AuthServiceDep,
) -> RedirectResponse:

    state: str = auth_service.generate_state()

    auth_url: str = auth_service.url_for_google(state)

    response = RedirectResponse(
        url=auth_url,
        status_code=302,
    )

    auth_service.set_state_cookie(response, state)

    return response


@app.get(
    path="/auth/google/callback",
    response_model=TokenResponse,
    summary="Handle Google OAuth2 callback",
)
async def google_callback(
    code: str,
    state: str,
    response: Response,
    http_client: HttpClientDep,
    auth_service: AuthServiceDep,
    oauth_state: str | None = Cookie(default=None),
) -> TokenResponse:

    auth_service.verify_state(
        returned_state=state,
        state_cookie=oauth_state,
        response=response,
    )

    google_tokens: dict[str, Any] = await auth_service.exchange_code_for_tokens(
        code, http_client
    )
    user_info: dict[str, Any] = await auth_service.fetch_user_info(
        google_tokens["access_token"], http_client
    )

    return auth_service.authenticate_oauth_user(
        provider="google",
        account_id=user_info["id"],
        email=user_info["email"],
        first_name=user_info.get("given_name", "Unknown"),
        last_name=user_info.get("family_name", "Unknown"),
    )

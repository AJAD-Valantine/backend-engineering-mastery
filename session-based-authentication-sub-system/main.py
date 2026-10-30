from typing import Any

from core.dependencies import (
    AuthServiceDep,
    CurrentUserDep,
    HttpClientDep,
    SessionCookieDep,
)
from fastapi import Cookie, FastAPI, Response, status
from fastapi.responses import RedirectResponse
from models.user import User
from schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
)
from schemas.user import UserCreateRequest, UserLoginRequest, UserResponse

app = FastAPI(title="Session-Auth")


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
    status_code=status.HTTP_200_OK,
    summary="Login to the application",
)
def login_user(
    response: Response,
    request_body: UserLoginRequest,
    auth_service: AuthServiceDep,
):
    return auth_service.authenticate_user(
        response,
        request_body.email,
        request_body.password
)


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


@app.post(
    path="/logout",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout from this device",
)
def logout(
    auth_service: AuthServiceDep,
    session_id: SessionCookieDep,
    response: Response,
    current_user: CurrentUserDep,
) -> None:

    auth_service.logout(session_id, response)


@app.post(
    path="/logout/all",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out all devices",
)
def logout_all(
    auth_service: AuthServiceDep,
    response: Response,
    current_user: CurrentUserDep,
) -> None:

    auth_service.logout_all(response, current_user.user_id)


@app.get(
    path="/sessions",
    status_code=status.HTTP_200_OK,
    summary="Get all active sessions for the current user",
)
def get_active_sessions(
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep,
) -> set[str]:

    return auth_service.get_active_sessions(current_user)


@app.delete(
    path="/sessions/{target_session_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out a specific session for the current user",
)
def logout_session(
    target_session_id: str,
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep,
) -> None:

    auth_service.logout_session(current_user, target_session_id)


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
    summary="Handle Google OAuth2 callback",
)
async def google_callback(
    code: str,
    state: str,
    response: Response,
    http_client: HttpClientDep,
    auth_service: AuthServiceDep,
    oauth_state: str | None = Cookie(default=None),
):

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
        response=response,
        email=user_info["email"],
        first_name=user_info.get("given_name", "Unknown"),
        last_name=user_info.get("family_name", "Unknown"),
    )

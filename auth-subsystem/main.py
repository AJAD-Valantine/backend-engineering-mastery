import secrets
import urllib.parse
from collections.abc import Sequence
from uuid import UUID

from core.database import Base, engine
from core.dependencies import AuthServiceDep, CurrentUserDep, HttpClientDep, SettingsDep
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from models.email_verification_token import EmailVerificationToken
from models.oauth_account import OAuthAccount
from models.password_reset_token import PasswordResetToken
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
def get_providers():
    return {"providers": ["google", "github"]}


@app.get(path="/auth/google", summary="Initiate Google OAuth2 flow")
def login_via_google(settings: SettingsDep):
    # 1. Generate a random state token for CSRF protection
    state = secrets.token_urlsafe(32)

    # 2. Build the authorization URL
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",  # OIDC scopes
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    )

    # 3. Redirect the user and set the state cookie
    response = RedirectResponse(url=auth_url)
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        max_age=600,  # Expires in 10 minutes
        samesite="lax",
    )
    return response


@app.get(path="/auth/github", summary="Initiate GitHub OAuth2 flow")
def login_via_github(settings: SettingsDep):
    state = secrets.token_urlsafe(32)

    params = {
        "client_id": settings.github_client_id,
        "redirect_uri": settings.github_redirect_uri,
        "response_type": "code",
        "scope": "user:email",  # GitHub's scope for reading emails
        "state": state,
    }
    auth_url = (
        f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(params)}"
    )

    response = RedirectResponse(url=auth_url)
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        max_age=600,
        samesite="lax",
    )
    return response


@app.get(
    path="/auth/google/callback",
    response_model=TokenResponse,
    summary="Handle Google OAuth2 callback",
)
async def google_callback(
    request: Request,
    code: str,
    state: str,
    settings: SettingsDep,
    http_client: HttpClientDep,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    # 1. Verify the state parameter against the cookie (CSRF Protection)
    cookie_state = request.cookies.get("oauth_state")
    if not cookie_state or state != cookie_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state token. Possible CSRF attack.",
        )

    # 2. Exchange the authorization code for a Google Access Token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret.get_secret_value(),
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.google_redirect_uri,
    }

    response = await http_client.post(token_url, data=token_data)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange authorization code with Google.",
        )

    google_tokens = response.json()
    google_access_token = google_tokens.get("access_token")

    # 3. Fetch Google User Profile
    user_info_response = await http_client.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {google_access_token}"},
    )
    user_info = user_info_response.json()

    # 4. Pass the data to your service layer
    return auth_service.authenticate_oauth_user(
        provider="google",
        account_id=user_info["id"],
        email=user_info["email"],
        first_name=user_info.get("given_name", "Unknown"),
        last_name=user_info.get("family_name", "Unknown"),
    )


@app.get(
    path="/auth/github/callback",
    response_model=TokenResponse,
    summary="Handle GitHub OAuth2 callback",
)
async def github_callback(
    request: Request,
    code: str,
    state: str,
    settings: SettingsDep,
    http_client: HttpClientDep,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    # 1. Verify the state parameter
    cookie_state = request.cookies.get("oauth_state")
    if not cookie_state or state != cookie_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state token. Possible CSRF attack.",
        )

    # 2. Exchange the code for a GitHub Access Token
    token_url = "https://github.com/login/oauth/access_token"
    token_data = {
        "client_id": settings.github_client_id,
        "client_secret": settings.github_client_secret.get_secret_value(),
        "code": code,
        "redirect_uri": settings.github_redirect_uri,
    }

    headers = {"Accept": "application/json"}
    response = await http_client.post(token_url, data=token_data, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange authorization code with GitHub.",
        )

    github_tokens = response.json()
    github_access_token = github_tokens.get("access_token")

    # 3. Fetch GitHub User Profile
    user_headers = {
        "Authorization": f"Bearer {github_access_token}",
        "Accept": "application/json",
    }
    user_info_response = await http_client.get(
        "https://api.github.com/user", headers=user_headers
    )
    user_info = user_info_response.json()

    email = user_info.get("email")
    if not email:
        emails_response = await http_client.get(
            "https://api.github.com/user/emails", headers=user_headers
        )
        emails = emails_response.json()
        email = next((e["email"] for e in emails if e["primary"]), emails[0]["email"])

    name_parts = (user_info.get("name") or user_info["login"]).split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    # 4. Pass the data to your service layer
    return auth_service.authenticate_oauth_user(
        provider="github",
        account_id=str(user_info["id"]),
        email=email,
        first_name=first_name,
        last_name=last_name,
    )

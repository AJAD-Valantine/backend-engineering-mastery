from fastapi import APIRouter, status, Depends, BackgroundTasks

from app.core.dependencies import OAuth2Form, get_auth_service
from app.core.email import send_password_reset_email
from app.schemas.auth import Token, ForgotPasswordRequest, ResetPasswordRequest
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

@auth_router.post(
    path="/forgot-password",
    status_code=status.HTTP_202_ACCEPTED
)
def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service),
):
    token = auth_service.request_password_reset(request.email)
    if token:
        background_tasks.add_task(send_password_reset_email, request.email, token)
    return {"message": "If an account exists with this email, you will receive reset instructions."}


@auth_router.post(
    path="/reset-password",
    status_code=status.HTTP_200_OK
)
def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    auth_service.reset_password(request.token, request.new_password)
    return {"message": "Password reset successfully"}